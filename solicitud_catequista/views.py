import json
from django.shortcuts import render, redirect
from .forms import SolicitudCatequistaForm
from .models import SolicitudCatequista
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .quickstart import enviar_email


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
    if not request.user.is_staff:
        return render(request, '403.html')

    if request.method == 'POST':
        data = json.loads(request.body)
        
        for asignacion in data:
            user_id = asignacion.get('userId')
            ciclo_asignado = asignacion.get('cicloAsignado')
            solicitud = SolicitudCatequista.objects.get(id=user_id)
            enviar_correo(solicitud.email, ciclo_asignado)
            
        return JsonResponse({'message': 'Asignaciones procesadas correctamente'})

    solicitudes = SolicitudCatequista.objects.all()
    return render(request, 'asignar_catequistas.html', {'solicitudes': solicitudes})


def enviar_correo(to, ciclo_asignado):
    sender="antoniopelaez2002@gmail.com"
    subject="Asignación de ciclo"
    message_text=f"Se te ha asignado el ciclo {ciclo_asignado}"
    enviar_email(sender, to, subject, message_text)


