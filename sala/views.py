from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Sala, Reserva, SolicitudReserva
from custom_user.models import CustomUser
from datetime import timedelta, date
from django.http import HttpResponse
from datetime import datetime
from .forms import SalaForm
import json

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

            todas_salas = Sala.objects.all()
            salas_ocupadas = todas_salas.filter(
                reserva__fecha=fecha,
                reserva__hora_inicio__lt=hora_fin,
                reserva__hora_fin__gt=hora_inicio
            )
            reservas_salas_ocupadas = Reserva.objects.filter(
                sala__in=salas_ocupadas,
                fecha=fecha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )
            
            return render(request, 'salas_disponibles.html', {'todas_salas':todas_salas,'salas_ocupadas': salas_ocupadas, 'reservas_salas_ocupadas':reservas_salas_ocupadas, 'fecha':fecha, 'fecha_hoy':date.today})

        return render(request, 'salas_disponibles.html', {'fecha_hoy':date.today})
    else:
        return redirect('/403')

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
                print('La hora de inicio debe ser menor a la hora de fin.')
                return HttpResponse('La hora de inicio debe ser menor a la hora de fin.')
            
            # Obtener usuario y sala
            usuario = CustomUser.objects.get(pk=usuario_id)
            sala = Sala.objects.get(pk=sala_id)
            
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
                reservas_exist = Reserva.objects.filter(sala=sala, fecha=proxima_fecha, hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
                if reservas_exist.exists():
                    print('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
                    lista_reservas.clear()
                    return HttpResponse('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
                
                reserva = Reserva(usuario=usuario, sala=sala, fecha=proxima_fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
                lista_reservas.append(reserva)
                proxima_fecha += timedelta(weeks=1)

            Reserva.objects.bulk_create(lista_reservas)
            
            return HttpResponse('Reservas creadas exitosamente.')  # O redirigir a una página de éxito

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

            reservas_exist = Reserva.objects.filter(sala=sala, fecha=fecha, hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
            if reservas_exist.exists():
                print('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
                return HttpResponse('Ya existe una reserva en el plazo seleccionado. La fecha ocupada es: ', reservas_exist.first().fecha)
            else:
                if sala.requiere_aprobacion:
                    print('La sala requiere aprobación. Se ha enviado una solicitud de reserva.')
                    solicitud = SolicitudReserva(usuario=request.user, sala=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
                    solicitud.save()
                else:
                    print('Reserva creada exitosamente.')
                    reserva = Reserva(usuario=request.user, sala=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
                    reserva.save()
                return redirect('mis_reservas')
    else:
        return redirect('/403')
    
@login_required
def mis_reservas(request):
    if request.user.is_coord or request.user.is_superuser:
        fecha_hoy = date.today()
        reservas_pasadas = Reserva.objects.filter(usuario=request.user, fecha__lt=fecha_hoy)
        reservas_futuras = Reserva.objects.filter(usuario=request.user, fecha__gte=fecha_hoy)
        solicitudes_de_reserva = SolicitudReserva.objects.filter(usuario=request.user, estado='pendiente')
        return render(request, 'mis_reservas.html', {'reservas_pasadas': reservas_pasadas, 'reservas_futuras':reservas_futuras, 'solicitudes_de_reserva':solicitudes_de_reserva, 'fecha_hoy':fecha_hoy})
    else:
        return redirect('/403')
    

@login_required
def listar_solicitudes_reserva(request):
    if request.user.is_superuser:
        solicitudes_pendientes = SolicitudReserva.objects.filter(estado = SolicitudReserva.EstadoChoices.PENDIENTE, fecha__gte=date.today())
        solicitudes_aceptadas = SolicitudReserva.objects.filter(estado = SolicitudReserva.EstadoChoices.ACEPTADA, fecha__gte=date.today())
        solicitudes_rechazadas = SolicitudReserva.objects.filter(estado = SolicitudReserva.EstadoChoices.RECHAZADA, fecha__gte=date.today())
        return render(request, 'solicitudes_reserva.html', {'solicitudes_pendientes': solicitudes_pendientes, 'solicitudes_aceptadas':solicitudes_aceptadas, 'solicitudes_rechazadas':solicitudes_rechazadas})
    else:
        return redirect('/403')

@login_required
def aprobar_solicitud_reserva(request, solicitud_id):
    if request.user.is_superuser:
        solicitud = get_object_or_404(SolicitudReserva, pk=solicitud_id)
        solicitud.estado = SolicitudReserva.EstadoChoices.ACEPTADA
        solicitud.save()

        reserva = Reserva(usuario=solicitud.usuario, sala=solicitud.sala, fecha=solicitud.fecha, hora_inicio=solicitud.hora_inicio, hora_fin=solicitud.hora_fin)
        reserva.save()
        return redirect('solicitudes_reserva')
    else:
        return redirect('/403')
    
@login_required
def rechazar_solicitud_reserva(request, solicitud_id):
    if request.user.is_superuser:
        solicitud = get_object_or_404(SolicitudReserva, pk=solicitud_id)
        solicitud.estado = SolicitudReserva.EstadoChoices.RECHAZADA
        solicitud.save()
        return redirect('solicitudes_reserva')
    else:
        return redirect('/403')

