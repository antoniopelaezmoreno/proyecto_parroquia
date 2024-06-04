from django.shortcuts import render, redirect, get_object_or_404
from grupo.models import Grupo
from datetime import date
from sesion.models import Sesion
from evento.models import Evento
from notificacion.models import Notificacion
from catecumeno.models import Catecumeno
from custom_user.models import CustomUser
from sala.models import Reserva
from solicitud_catequista.models import SolicitudCatequista
from curso.models import Curso
from sesion.views import contar_ausencias, contar_ausencias_ultima_sesion, catecumenos_desde_catequista
from django.contrib.auth.decorators import login_required
from django.db import DEFAULT_DB_ALIAS
from django.urls import reverse
from solicitud_catequista.quickstart import enviar_email
from django.http import HttpResponseRedirect
from correo.views import conseguir_credenciales

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(destinatario=request.user, visto=False)
        if request.user.is_superuser:
            proximo_evento = Evento.objects.filter(fecha__gte=date.today()).order_by('fecha').first()
            num_catecumenos = Catecumeno.objects.all().count()
            num_catequistas = CustomUser.objects.all().exclude(is_superuser=True).count()
            num_solicitudes = SolicitudCatequista.objects.filter(ciclo_asignado__isnull=True).count()
            return render(request, 'index/index_admin.html', {'proximo_evento':proximo_evento,'notificaciones': notificaciones, 'num_catecumenos': num_catecumenos, 'num_catequistas': num_catequistas, 'num_solicitudes': num_solicitudes})
        elif request.user.is_coord:
            proxima_sesion = Sesion.objects.filter(ciclo = request.user.ciclo).filter(fecha__gte=date.today()).order_by('fecha').first()
            proximo_evento = Evento.objects.filter(participantes=request.user).filter(fecha__gte=date.today()).order_by('fecha').first()
            num_catecumenos = Catecumeno.objects.filter(ciclo=request.user.ciclo).count()
            ausencias= contar_ausencias(request)
            ausencias_ultima_sesion = contar_ausencias_ultima_sesion(request)
            if proxima_sesion:
                archivos_sesion = proxima_sesion.archivos.all()
            else:
                archivos_sesion = None
            return render(request, 'index/index_coord.html', {'proxima_sesion': proxima_sesion, 'archivos_sesion': archivos_sesion,'proximo_evento':proximo_evento,'notificaciones': notificaciones, 'num_catecumenos': num_catecumenos, 'ausencias': ausencias, 'ausencias_ultima_sesion': ausencias_ultima_sesion})
        
        else:
            proxima_sesion = Sesion.objects.filter(ciclo = request.user.ciclo).filter(fecha__gte=date.today()).order_by('fecha').first()
            proximo_evento = Evento.objects.filter(participantes=request.user).filter(fecha__gte=date.today()).order_by('fecha').first()
            num_catecumenos = len(catecumenos_desde_catequista(request.user))
            num_ausencias= contar_ausencias(request).count()
            num_ausencias_ultima_sesion = len(contar_ausencias_ultima_sesion(request))
            if proxima_sesion:
                archivos_sesion = proxima_sesion.archivos.all()
            else:
                archivos_sesion = None
            return render(request, 'index/index_cat.html', {'proxima_sesion': proxima_sesion, 'archivos_sesion': archivos_sesion,'proximo_evento':proximo_evento,'notificaciones': notificaciones, 'num_catecumenos': num_catecumenos, 'num_ausencias': num_ausencias, 'num_ausencias_ultima_sesion': num_ausencias_ultima_sesion})
    else:
        choices = Catecumeno.CicloChoices.choices
        return render(request, 'index/index.html', {'choices': choices})

def c403(request):
    return render(request, '403.html', status=403)

def c404(request):
    return render(request, '404.html', status=404)

def c500(request):
    return render(request, '500.html', status=500)

def error(request, mensaje):
    return render(request, 'error.html', {'mensaje': mensaje})

@login_required
def terminar_curso(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            SolicitudCatequista.objects.all().delete()
            Catecumeno.objects.all().delete()
            usuarios = CustomUser.objects.all().exclude(is_superuser=True)
            for usuario in usuarios:
                enviar_correo_renovacion(request, usuario.email)
                usuario.delete()

            Grupo.objects.all().delete()
            Evento.objects.all().delete()
            Notificacion.objects.all().delete()
            Reserva.objects.all().delete()
            ultimo_curso = Curso.objects.latest('id')
            primer_año = int(ultimo_curso.curso.split('-')[0])
            segundo_año = int(ultimo_curso.curso.split('-')[1])
            nombre_curso = f'{primer_año+1}-{segundo_año+1}'
            Curso.objects.create(curso=nombre_curso)

            return redirect('/')
        else:
            request.session['redirect_to'] = '/terminar_curso'
            creds=conseguir_credenciales(request, request.user)
            if isinstance(creds, HttpResponseRedirect):
                return creds
            return render(request, 'confirmar_terminar_curso.html')
    else:
        return redirect('/403')

@login_required
def enviar_correo_renovacion(request, to):
    sender = "antoniopelaez2002@gmail.com"
    subject="Renovación de catequista"
    url = reverse('crear_solicitud_catequista')
    enlace = request.build_absolute_uri(url)
    message_text = f'Haga clic para volver a solicitar ser catequista: {enlace}'
    enviar_email(request, sender, to, subject, message_text, request.user)

@login_required
def notificar_familias_ultima_ausencia(request, catecumeno_id):
    catecumeno = get_object_or_404(Catecumeno, pk=catecumeno_id)
    if request.user.is_superuser or (request.user.is_coord and catecumeno.ciclo == request.user.ciclo):
        creds=conseguir_credenciales(request, request.user)
        if isinstance(creds, HttpResponseRedirect):
            return creds
        
        sender = request.user.email
        subject="Ausencia a catequesis de su hijo " + catecumeno.nombre + " " + catecumeno.apellidos
        message_text = """
        Estimada familia,
        Nos ponemos en contacto con ustedes para notificarle que su hijo/a, """ + catecumeno.nombre + " " + catecumeno.apellidos + """, ha faltado a la última sesión de catequesis y no hemos recibido justificación al respecto.
        Atentamente,
        El equipo de catequesis.
        """
        if catecumeno.email_madre == catecumeno.email_padre:
            enviar_email(request, sender, catecumeno.email_madre, subject, message_text, request.user)
        else:
            enviar_email(request, sender, catecumeno.email_madre, subject, message_text, request.user)
            enviar_email(request, sender, catecumeno.email_padre, subject, message_text, request.user)
        return redirect('/panel_ultimas_ausencias')
    else:
        return redirect('/403')

@login_required
def notificar_familias_ausencias_reiteradas(request, catecumeno_id):
    catecumeno = get_object_or_404(Catecumeno, pk=catecumeno_id)
    if request.user.is_superuser or (request.user.is_coord and catecumeno.ciclo == request.user.ciclo):
        creds=conseguir_credenciales(request, request.user)
        if isinstance(creds, HttpResponseRedirect):
            return creds
        
        sender = request.user.email
        subject="Ausencias reiteradas a catequesis de su hijo " + catecumeno.nombre + " " + catecumeno.apellidos
        message_text = """
        Estimada familia,
        Nos ponemos en contacto con ustedes para notificarle que su hijo/a, """ + catecumeno.nombre + " " + catecumeno.apellidos + """, ha faltado ya más de tres veces en este curso.
        Nos vemos en la obligación de recordarles que la asistencia a catequesis es obligatoria y que, en caso de no poder asistir, deben justificar la ausencia.
        Atentamente,
        El equipo de catequesis.
        """
        if catecumeno.email_madre == catecumeno.email_padre:
            enviar_email(request, sender, catecumeno.email_madre, subject, message_text, request.user)
        else:
            enviar_email(request, sender, catecumeno.email_madre, subject, message_text, request.user)
            enviar_email(request, sender, catecumeno.email_padre, subject, message_text, request.user)
        return redirect('/panel_ausencias_reiteradas')
    else:
        return redirect('/403')



@login_required
def panel_ciclos(request):
    if request.user.is_superuser:
        ciclos = Catecumeno.CicloChoices.choices
        catequistas = CustomUser.objects.all().exclude(is_superuser=True)
        return render(request, 'panel_ciclos.html', {'ciclos': ciclos, 'catequistas': catequistas})
    else:
        return redirect('/403')
    
@login_required
def panel_ultimas_ausencias(request):
    if request.user.is_coord:
        lista_ausentes = contar_ausencias_ultima_sesion(request)
        return render(request, 'panel_ultimas_ausencias.html', {'lista_ausentes': lista_ausentes})
    else:
        return redirect('/403')

@login_required
def panel_ausencias_reiteradas(request):
    if request.user.is_coord:
        lista_ausentes = contar_ausencias(request)
        return render(request, 'panel_ausencias_reiteradas.html', {'lista_ausentes': lista_ausentes})
    else:
        return redirect('/403')
    
def pantalla_confirmacion_exito(request):
    return render(request, 'confirmacion_exito.html')