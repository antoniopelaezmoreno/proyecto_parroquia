from django.shortcuts import render, redirect
from grupo.models import Grupo
from datetime import date
from sesion.models import Sesion
from notificacion.models import Notificacion

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(destinatario=request.user, visto=False)
        if request.user.is_coord:
            proxima_sesion = Sesion.objects.filter(ciclo = request.user.ciclo).filter(fecha__gte=date.today()).order_by('fecha').first()
            if proxima_sesion:
                archivos_sesion = proxima_sesion.files.all()
            else:
                archivos_sesion = None
            grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
            return render(request, 'index/index_coord.html', {'grupos': grupos, 'proxima_sesion': proxima_sesion, 'archivos_sesion': archivos_sesion,'notificaciones': notificaciones})
        elif request.user.is_superuser:
            return render(request, 'index/index_admin.html')
        else:
            return render(request, 'index/index_cat.html')
    else:
        return render(request, 'index/index.html')

def c403(request):
    return render(request, '403.html')

def c404(request):
    return render(request, '404.html')

def error(request, mensaje):
    return render(request, 'error.html', {'mensaje': mensaje})