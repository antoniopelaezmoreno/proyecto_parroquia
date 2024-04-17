
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento
from sala.models import Sala, Reserva
import re
from datetime import  date
from datetime import datetime
from django.http import HttpResponse
from custom_user.models import CustomUser

@login_required
def crear_evento(request):
    if request.user.is_coord or request.user.is_superuser:
        tipo_choices = Evento.TIPO_CHOICES.choices
        usuarios = CustomUser.objects.all()
        if request.method == 'POST':
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            sala_necesaria = request.POST.get('sala_necesaria')
            participantes_seleccionados = request.POST.getlist('participantes')
            print(participantes_seleccionados)
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion')

            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha) or hora_inicio is None or hora_fin is None:
                return render(request, 'salas_disponibles.html', {'fecha_hoy':date.today, 'error': 'Por favor, introduzca todos los campos'})
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
            
            if sala_necesaria:         
                return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios, 'todas_salas':todas_salas,'salas_ocupadas': salas_ocupadas, 'reservas_salas_ocupadas':reservas_salas_ocupadas, 'participantes_seleccionados':participantes_seleccionados})
            else:
                evento = Evento(fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, tipo = tipo, nombre=nombre, descripcion=descripcion)
                evento.save()
                evento.participantes.set(participantes_seleccionados)
                evento.save()
                return redirect('/')

        return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios})
    else:
        return redirect('/403')
    
@login_required
def nuevo_evento(request):
    if request.user.is_coord or request.user.is_superuser:
        if request.method == 'POST':
            sala_id = request.POST.get('sala_id')
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion')
            participantes = request.POST.get('participantes')
            participantes = map(int, participantes.split(','))  # Convertir los IDs de participantes a números enteros
            participantes = list(participantes)
            print(participantes)

            if fecha < str(datetime.now().date()):
                print('No se puede crear una evento para una fecha pasada.')
                return HttpResponse('No se puede crear una evento para una fecha pasada.')
            elif hora_inicio >= hora_fin:
                print('La hora de inicio debe ser menor a la hora de fin.')
                return HttpResponse('La hora de inicio debe ser menor a la hora de fin.')

            sala = get_object_or_404(Sala, pk=sala_id)

            evento = Evento(sala_reservada=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, tipo = tipo, nombre=nombre, descripcion=descripcion)
            evento.save()
            evento.participantes.set(participantes)
            evento.save()
            return redirect('/')
        else:
            return redirect('/404')
    else:
        return redirect('/403')

