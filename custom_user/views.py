from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import CustomUser
from solicitud_catequista.models import SolicitudCatequista
from .forms import CustomUserForm
from catecumeno.models import Catecumeno


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

def listar_catequistas(request):
    if request.user.is_superuser:
        catequistas = CustomUser.objects.all()
        return render(request, 'listar_catequistas_admin.html', {'catequistas': catequistas})
    elif request.user.is_coord:
        ciclo=request.user.ciclo
        catequistas = CustomUser.objects.filter(ciclo=ciclo)
        return render(request, 'listar_catequistas.html', {'catequistas': catequistas})
    else:
        return render(request, '403.html')
    
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


def crear_grupo(request):
    if request.user.is_authenticated:
        if request.user.is_coord:
            ciclo = request.user.ciclo
            catequistas = CustomUser.objects.filter(ciclo=ciclo)
            if request.method == 'POST':
                form = GrupoForm(request.POST, request.FILES, catequistas=catequistas)
                if form.is_valid():
                    grupo = form.save()
                    return redirect('/')
            else:
                form = GrupoForm(catequistas=catequistas)
            return render(request, 'crear_grupo.html', {'form': form, 'ciclo': ciclo})
        if request.user.is_superuser:
            return redirect('/catecumeno/crear_grupo/posco_1')
        else:
            return render(request, '403.html')
    else:
        return render(request, '403.html')
    
def crear_grupo_admin(request, ciclo):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            valores_ciclo = [choice[0] for choice in Catecumeno.CicloChoices.choices]
            if ciclo not in valores_ciclo:
                return render(request, '404.html')
            catequistas = CustomUser.objects.filter(ciclo=ciclo)
            if request.method == 'POST':
                form = GrupoForm(request.POST, request.FILES, catequistas=catequistas)
                if form.is_valid():
                    grupo = form.save()
                    return redirect('/')
            else:
                form = GrupoForm(catequistas=catequistas)
            return render(request, 'crear_grupo.html', {'form': form, 'ciclo': ciclo})
        else:
            return render(request, '403.html')
    else:
        return render(request, '403.html')
