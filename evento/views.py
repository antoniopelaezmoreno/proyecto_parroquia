
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento
from sala.models import Sala, Reserva
import re
from datetime import datetime
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from custom_user.models import CustomUser
from sesion.models import Sesion
from correo.views import conseguir_credenciales
from googleapiclient.discovery import build

@login_required
def crear_evento(request):
    if request.user.is_coord or request.user.is_superuser:

        request.session['redirect_to'] = request.path
        creds= conseguir_credenciales(request, request.user)
        if isinstance(creds, HttpResponseRedirect):
            return creds
        tipo_choices = Evento.TIPO_EVENTO.choices
        usuarios = CustomUser.objects.all()
        participantes_seleccionados=[]
        if request.method == 'POST':
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            sala_necesaria = request.POST.get('sala_necesaria')
            participantes_seleccionados = request.POST.getlist('participantes')
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion')

            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha) or hora_inicio is None or hora_fin is None:
                return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices,'error': 'Por favor, introduzca todos los campos', 'usuarios':usuarios, 'participantes_seleccionados':participantes_seleccionados})
            todas_salas = Sala.objects.filter(requiere_aprobacion=False)
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
            
            if sala_necesaria:         
                return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios, 'todas_salas':todas_salas,'salas_ocupadas': salas_ocupadas, 'reservas_salas_ocupadas':reservas_salas_ocupadas, 'participantes_seleccionados':participantes_seleccionados})
            else:
                evento = Evento(fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, tipo = tipo, nombre=nombre, descripcion=descripcion)
                evento.save()
                evento.participantes.set(participantes_seleccionados)
                evento.save()

                asociar_a_google_calendar(request, evento, request.user)
                return redirect('/')

        if request.GET.get('reunion_comision') and request.user.is_superuser:
            # Crear el evento automáticamente con los detalles predefinidos
            nombre = "Reunión de Comisión"
            tipo = Evento.TIPO_EVENTO.REUNION
            coordinadores = CustomUser.objects.filter(is_coord=True)
            participantes_seleccionados = list(coordinadores.values_list('id', flat=True))
            
            return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios, 'participantes_seleccionados':participantes_seleccionados, 'tipo_seleccionado': tipo, 'nombre': nombre})
        
        if request.GET.get('reunion_ciclo') and request.user.is_coord:
            # Crear el evento automáticamente con los detalles predefinidos
            ciclo = request.user.ciclo
            nombre = "Reunión de " + ciclo
            tipo = Evento.TIPO_EVENTO.REUNION
            catequistas = CustomUser.objects.filter(ciclo=ciclo)
            participantes_seleccionados = list(catequistas.values_list('id', flat=True))
            
            return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios, 'participantes_seleccionados':participantes_seleccionados, 'tipo_seleccionado': tipo, 'nombre': nombre})
        return render(request, 'crear_evento.html', {'tipo_choices': tipo_choices, 'usuarios':usuarios, 'participantes_seleccionados':participantes_seleccionados})
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
            if not participantes == "":
                participantes = map(int, participantes.split(','))  # Convertir los IDs de participantes a números enteros
                participantes = list(participantes)

            if fecha < str(datetime.now().date()):
                return HttpResponse('No se puede crear una evento para una fecha pasada.')
            elif hora_inicio >= hora_fin:
                return HttpResponse('La hora de inicio debe ser menor a la hora de fin.')

            sala = get_object_or_404(Sala, pk=sala_id)

            if sala.requiere_aprobacion:
                return HttpResponse('No se puede crear un evento en una sala que requiere aprobación.')

            evento = Evento(sala_reservada=sala, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, tipo = tipo, nombre=nombre, descripcion=descripcion)
            evento.save()
            evento.participantes.set(participantes)
            evento.save()

            asociar_a_google_calendar(request, evento, request.user)

            return redirect('/')
        else:
            return redirect('/404')
    else:
        return redirect('/403')


def asociar_a_google_calendar(request, evento, user):
    creds = conseguir_credenciales(request, user)
    if isinstance(creds, HttpResponseRedirect):
        return creds
    event={
        'summary': evento.nombre,
        'description': evento.descripcion,
        'start': {
            'dateTime': str(evento.fecha) + 'T' + str(evento.hora_inicio) + ':00',
            'timeZone': 'Europe/Madrid',
        },
        'end': {
            'dateTime': str(evento.fecha) + 'T' + str(evento.hora_fin) + ':00',
            'timeZone': 'Europe/Madrid',
        }
    }
    if evento.participantes:
        event['attendees']=[{'email': usuario.email} for usuario in evento.participantes.all()]
    
    if evento.sala_reservada:
        event['location']=evento.sala_reservada.nombre

    try:
        service = build("calendar", "v3", credentials=creds)
        event=service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print('Error creating event: %s' % (e))


@login_required
def obtener_eventos(request):
    eventos = Evento.objects.filter(participantes=request.user)
    if request.user.is_superuser:
        eventos = Evento.objects.all()
    eventos_data = [{
        'id': evento.id,
        'title': evento.nombre,
        'start': evento.fecha.strftime('%Y-%m-%dT'+evento.hora_inicio.strftime('%H:%M:%S')),
        'end': evento.fecha.strftime('%Y-%m-%dT'+evento.hora_fin.strftime('%H:%M:%S')),
        'color': '#2c36bd' if evento.tipo == Evento.TIPO_EVENTO.REUNION else ('green' if evento.tipo ==  Evento.TIPO_EVENTO.CONVIVENCIA else '#c02424'),
        'tipo': 'Evento',
        'description': evento.descripcion,
        'sala_reservada': evento.sala_reservada.nombre if evento.sala_reservada else None
    } for evento in eventos]

    sesiones = Sesion.objects.filter(ciclo=request.user.ciclo)
    sesiones_data = [{
        'title': sesion.titulo,
        'start': sesion.fecha.strftime('%Y-%m-%dT'+sesion.hora_inicio.strftime('%H:%M:%S')),
        'end': sesion.fecha.strftime('%Y-%m-%dT'+sesion.hora_fin.strftime('%H:%M:%S')),
        'color': '#e8ca13',
        'tipo': 'Sesión',
        'description': sesion.descripcion
    } for sesion in sesiones]

    eventos_data.extend(sesiones_data)

    return JsonResponse(eventos_data, safe=False)

@login_required
def mostrar_eventos(request):
    if request.user.is_superuser:
        eventos = Evento.objects.all().order_by('fecha')
    else:
        eventos=Evento.objects.filter(participantes=request.user).order_by('fecha')
    return render(request, 'mostrar_eventos.html', {'eventos': eventos})
    
@login_required
def detalles_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.user.is_superuser or request.user in evento.participantes.all():
        return render(request, 'detalles_evento.html', {'evento': evento})
    else:
        return redirect('/403')
