from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render

# Create your views here.
def iniciar_sesion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirige a una página exitosa
        else:
            return HttpResponse('Credenciales inválidas. Inténtalo de nuevo.')
    return HttpResponse('Método no permitido.')

def cerrar_sesion(request):
    logout(request)
    return redirect('/')