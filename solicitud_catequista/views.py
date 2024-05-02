import json
from django.shortcuts import render, redirect
from .forms import SolicitudCatequistaForm
from .models import SolicitudCatequista
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .quickstart import enviar_email
from django.urls import reverse
from correo.views import conseguir_credenciales
from django.http import HttpResponseRedirect

# Create your views here.
def crear_solicitud_cateqista(request):
    if request.method == 'POST':
        form = SolicitudCatequistaForm(request.POST, request.FILES)
        if form.is_valid():
            catecumeno = form.save()
            return redirect('/') 
    else:
        form = SolicitudCatequistaForm()
    
    return render(request, 'crear_solicitud_catequista.html', {'form': form})

@csrf_exempt
def asignar_catequistas(request):
    if not request.user.is_superuser:
        return redirect('/403')

    request.session['redirect_to'] = request.path
    creds = conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds
    if request.method == 'POST':
        data = json.loads(request.body)
        
        for asignacion in data:
            user_id = asignacion.get('userId')
            ciclo_asignado = asignacion.get('cicloAsignado')
            solicitud = SolicitudCatequista.objects.get(id=user_id)
            enviar_correo_solicitud(request,solicitud.email,user_id, ciclo_asignado, request.user)
            
        return JsonResponse({'message': 'Asignaciones procesadas correctamente'})

    solicitudes = SolicitudCatequista.objects.all()
    return render(request, 'asignar_catequistas.html', {'solicitudes': solicitudes})


def enviar_correo_solicitud(request, to, solicitud_id, ciclo, user):
    sender = "antoniopelaez2002@gmail.com"
    subject="Asignación de ciclo"
    url = reverse('crear_usuario_desde_solicitud', args=[solicitud_id, ciclo])
    enlace = request.build_absolute_uri(url)
    message_text = f'Haga clic en el siguiente enlace para completar su registro: {enlace}'
    enviar_email(request, sender, to, subject, message_text, user)