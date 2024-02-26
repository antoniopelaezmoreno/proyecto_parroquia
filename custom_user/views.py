from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import CustomUser


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
