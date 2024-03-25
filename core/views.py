from django.shortcuts import render, redirect
from grupo.models import Grupo
from datetime import date
from sesion.models import Sesion

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.is_coord:
            proxima_sesion = Sesion.objects.filter(ciclo = request.user.ciclo).filter(fecha__gte=date.today()).order_by('fecha').first()
            grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
            return render(request, 'index/index_coord.html', {'grupos': grupos, 'proxima_sesion': proxima_sesion})
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