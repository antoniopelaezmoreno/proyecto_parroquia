from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Sala, Reserva
from custom_user.models import CustomUser
from datetime import timedelta, date
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from .forms import SalaForm
import json
import re
from django.urls import reverse

@login_required
def crear_sala(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = SalaForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = SalaForm()
        
        return render(request, 'crear_sala.html', {'form': form})
    else:
        return redirect('/403')

@login_required
def obtener_salas_disponibles(request):
    if request.user.is_coord or request.user.is_superuser:
        if request.method == 'POST':
            fecha = request.POST.get('fecha')
            
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')

            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha) or hora_inicio is None or hora_fin is None:
                return render(request, 'salas_disponibles.html', {'fecha_hoy':date.today, 'error': 'Por favor, introduzca todos los campos'})
            todas_salas = Sala.objects.all()
            salas_ocupadas = todas_salas.filter(
                reserva__fecha=fecha,
                reserva__hora_inicio__lt=hora_fin,
                reserva__hora_fin__gt=hora_inicio,
                reserva__estado=Reserva.EstadoChoices.ACEPTADA
            )
            reservas_salas_ocupadas = Reserva.objects.filter(
                sala__in=salas_ocupadas,
                fecha=fecha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
                estado=Reserva.EstadoChoices.ACEPTADA
            )
            
            return render(request, 'salas_disponibles.html', {'todas_salas':todas_salas,'salas_ocupadas': salas_ocupadas, 'reservas_salas_ocupadas':reservas_salas_ocupadas, 'fecha':fecha, 'fecha_hoy':date.today})

        return render(request, 'salas_disponibles.html', {'fecha_hoy':date.today})
    else:
        return redirect('/403')

from django.contrib import messages

@login_required
def crear_reservas_por_defecto(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            usuario_id = request.POST.get('usuario')
            sala_id = request.POST.get('sala')
            dia_semana = int(request.POST.get('dia_semana'))
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            if hora_inicio >= hora_fin:
                messages.error(request, 'La hora de inicio debe ser menor a la hora de fin.')
                return redirect('crear_reservas')  # Reemplaza 'nombre_de_la_url' con el nombre de la URL a la que deseas redirigir

            # Obtener usuario y sala
            usuario = get_object_or_404(CustomUser, pk=usuario_id)
            sala = get_object_or_404(Sala, pk=sala_id)

            # Obtener la fecha actual
            fecha_actual = date.today()

            # Calcular la fecha del próximo día de la semana elegido
            dia_actual = fecha_actual.weekday()
            dias_para_dia_elegido = (dia_semana - dia_actual + 7) % 7
            proxima_fecha = fecha_actual + timedelta(days=dias_para_dia_elegido)

            # Calcular la fecha límite (30 de junio)
            fecha_limite = date(fecha_actual.year, 6, 30)

            lista_reservas = []
            # Crear reservas hasta la fecha límite (30 de junio) para cada viernes
            while proxima_fecha <= fecha_limite:
                reservas_exist = Reserva.objects.filter(sala=sala, fecha=proxima_fecha, hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio, estado=Reserva.EstadoChoices.ACEPTADA)
                if reservas_exist.exists():
                    messages.error(request, f'Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: {reservas_exist.first().fecha}')
                    return redirect('crear_reservas')  # Reemplaza 'nombre_de_la_url' con el nombre de la URL a la que deseas redirigir
                
                reserva = Reserva(usuario=usuario, sala=sala, fecha=proxima_fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
                lista_reservas.append(reserva)
                proxima_fecha += timedelta(weeks=1)

            Reserva.objects.bulk_create(lista_reservas)
            
            messages.success(request, 'Reservas creadas exitosamente.')
            return redirect('crear_reservas')  # Reemplaza 'nombre_de_la_url' con el nombre de la URL a la que deseas redirigir

        salas = Sala.objects.all()
        usuarios = CustomUser.objects.filter(is_coord=True)
        return render(request, 'crear_reservas.html', {'salas': salas, 'usuarios': usuarios})
    else:
        return redirect('/403')

    
@login_required
def reservar_sala(request):
    if request.user.is_coord or request.user.is_superuser:
        if request.method == 'POST':
            sala_id = request.POST.get('sala_id')
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')

            if fecha < str(datetime.now().date()):
                print('No se puede reservar una sala para una fecha pasada.')
                return HttpResponse('No se puede reservar una sala para una fecha pasada.')
            elif hora_inicio >= hora_fin:
                print('La hora de inicio debe ser menor a la hora de fin.')
                return HttpResponse('La hora de inicio debe ser menor a la hora de fin.')

            sala = get_object_or_404(Sala, pk=sala_id)

            reservas_exist = Reserva.objects.filter(sala=sala, fecha=fecha, hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio, estado=Reserva.EstadoChoices.ACEPTADA)
            if reservas_exist.exists():
                print('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
                return HttpResponse('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
            else:
                if sala.requiere_aprobacion:
                    print('La sala requiere aprobación. Se ha enviado una solicitud de reserva.')
                    motivo = request.POST.get('motivo')
                    if len(motivo) > 250:
                        return HttpResponse('El motivo no puede tener más de 250 caracteres.')
                    reserva = Reserva(usuario=request.user, sala=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, motivo=motivo, estado=Reserva.EstadoChoices.PENDIENTE)
                    reserva.save()
                else:
                    print('Reserva creada exitosamente.')
                    reserva = Reserva(usuario=request.user, sala=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, estado=Reserva.EstadoChoices.ACEPTADA)
                    reserva.save()
                return redirect('mis_reservas')
        else:
            return redirect('/404')
    else:
        return redirect('/403')
    
@login_required
def mis_reservas(request):
    if request.user.is_coord or request.user.is_superuser:
        error_reserva_pasada = request.session.pop('reserva_pasada', None)
        fecha_hoy = date.today()
        reservas_pasadas = Reserva.objects.filter(usuario=request.user, fecha__lt=fecha_hoy, estado='aceptada').order_by('fecha')
        reservas_futuras = Reserva.objects.filter(usuario=request.user, fecha__gte=fecha_hoy, estado='aceptada').order_by('fecha')
        solicitudes_de_reserva = Reserva.objects.filter(usuario=request.user, estado='pendiente').order_by('fecha')
        return render(request, 'mis_reservas.html', {'reservas_pasadas': reservas_pasadas, 'reservas_futuras':reservas_futuras, 'solicitudes_de_reserva':solicitudes_de_reserva, 'fecha_hoy':fecha_hoy, 'error_reserva_pasada':error_reserva_pasada})
    else:
        return redirect('/403')
    

@login_required
def listar_solicitudes_reserva(request):
    if request.user.is_superuser:
        error = request.session.pop('error', None)
        solicitudes_pendientes = Reserva.objects.filter(estado = Reserva.EstadoChoices.PENDIENTE, fecha__gte=date.today())
        solicitudes_aceptadas = Reserva.objects.filter(estado = Reserva.EstadoChoices.ACEPTADA, fecha__gte=date.today(), sala__requiere_aprobacion=True)
        solicitudes_rechazadas = Reserva.objects.filter(estado = Reserva.EstadoChoices.RECHAZADA, fecha__gte=date.today())
        return render(request, 'solicitudes_reserva.html', {'solicitudes_pendientes': solicitudes_pendientes, 'solicitudes_aceptadas':solicitudes_aceptadas, 'solicitudes_rechazadas':solicitudes_rechazadas, 'error':error})
    else:
        return redirect('/403')

@login_required
def aprobar_solicitud_reserva(request, solicitud_id):
    if request.user.is_superuser:
        solicitud = get_object_or_404(Reserva, pk=solicitud_id)
        
        reservas_exist = Reserva.objects.filter(sala=solicitud.sala, fecha=solicitud.fecha, hora_inicio__lt=solicitud.hora_fin, hora_fin__gt=solicitud.hora_inicio, estado=Reserva.EstadoChoices.ACEPTADA).exclude(pk=solicitud_id)
                
        if reservas_exist.exists():
            solicitud.estado = Reserva.EstadoChoices.RECHAZADA
            solicitud.save()
            request.session['error'] = "Ya hay una reserva para esa sala en ese horario."
            return redirect('/sala/solicitudes/')
        
        Reserva.objects.filter(sala=solicitud.sala, fecha=solicitud.fecha, hora_inicio__lt=solicitud.hora_fin, hora_fin__gt=solicitud.hora_inicio, estado=Reserva.EstadoChoices.PENDIENTE).exclude(pk=solicitud_id).update(estado=Reserva.EstadoChoices.RECHAZADA)
        solicitud.estado = Reserva.EstadoChoices.ACEPTADA
        solicitud.save()
        return redirect('solicitudes_reserva')
    else:
        return redirect('/403')
    
@login_required
def rechazar_solicitud_reserva(request, solicitud_id):
    if request.user.is_superuser:
        solicitud = get_object_or_404(Reserva, pk=solicitud_id)
        solicitud.estado = Reserva.EstadoChoices.RECHAZADA
        solicitud.save()
        return redirect('solicitudes_reserva')
    else:
        return redirect('/403')
    

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    if (request.user.is_coord and reserva.usuario == request.user) or request.user.is_superuser:
        if reserva.fecha < date.today():
            request.session['reserva_pasada'] = "No se puede cancelar una reserva pasada"
            return redirect('mis_reservas')
        reserva.delete()
        return redirect('mis_reservas')
    else:
        return redirect('/403')

