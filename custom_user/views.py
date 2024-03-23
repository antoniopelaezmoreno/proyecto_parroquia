from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import CustomUser
from solicitud_catequista.models import SolicitudCatequista
from .forms import CustomUserForm
from catecumeno.models import Catecumeno
from google_auth_oauthlib.flow import InstalledAppFlow
from django.contrib.auth.decorators import login_required
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]


def iniciar_sesion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/') 
        else:
            return HttpResponse('Credenciales inválidas. Inténtalo de nuevo.')
    return HttpResponse('Método no permitido.')

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required
def listar_catequistas(request):
    if request.user.is_superuser:
        catequistas = CustomUser.objects.all()
        return render(request, 'listar_catequistas_admin.html', {'catequistas': catequistas})
    elif request.user.is_coord:
        ciclo=request.user.ciclo
        catequistas = CustomUser.objects.filter(ciclo=ciclo)
        return render(request, 'listar_catequistas.html', {'catequistas': catequistas})
    else:
        return redirect('/403')
    
def crear_usuario_desde_solicitud(request, id, ciclo):
    solicitud = SolicitudCatequista.objects.get(id=id)
    

    if request.method == 'POST':
        # Si se envió un formulario, procesar los datos
        form = CustomUserForm(request.POST)
        if form.is_valid():
            # Crear un nuevo CustomUser a partir de los datos del formulario
            custom_user = form.save(commit=False)
            custom_user.first_name = solicitud.nombre
            custom_user.last_name = solicitud.apellidos
            custom_user.email = solicitud.email
            custom_user.ciclo = ciclo
                # Save the credentials for the next run
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8081)
            custom_user.token_json = creds.to_json()
            custom_user.save()
            
            # Eliminar la solicitud de catequista
            solicitud.delete()
            
            # Redirigir a una página de éxito o a donde sea apropiado
            return redirect('/')  # Cambia 'exito' por el nombre de la URL de la página de éxito
            
    else:
        # Si es una solicitud GET, mostrar el formulario
        form = CustomUserForm()
    
    # Renderizar el formulario para la creación de un CustomUser
    return render(request, 'crear_usuario_desde_solicitud.html', {'form': form})