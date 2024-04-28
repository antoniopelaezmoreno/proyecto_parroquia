from django.shortcuts import render, redirect
from grupo.models import Grupo
from datetime import date
from sesion.models import Sesion
from evento.models import Evento
from notificacion.models import Notificacion
from catecumeno.models import Catecumeno
from sesion.views import contar_ausencias, contar_ausencias_ultima_sesion

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(destinatario=request.user, visto=False)
        if request.user.is_coord:
            proxima_sesion = Sesion.objects.filter(ciclo = request.user.ciclo).filter(fecha__gte=date.today()).order_by('fecha').first()
            proximo_evento = Evento.objects.filter(participantes=request.user).filter(fecha__gte=date.today()).order_by('fecha').first()
            num_catecumenos = Catecumeno.objects.filter(ciclo=request.user.ciclo).count()
            num_ausencias= contar_ausencias(request).count()
            num_ausencias_ultima_sesion = len(contar_ausencias_ultima_sesion(request))
            if proxima_sesion:
                archivos_sesion = proxima_sesion.files.all()
            else:
                archivos_sesion = None
            grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
            return render(request, 'index/index_coord.html', {'grupos': grupos, 'proxima_sesion': proxima_sesion, 'archivos_sesion': archivos_sesion,'proximo_evento':proximo_evento,'notificaciones': notificaciones, 'num_catecumenos': num_catecumenos, 'num_ausencias': num_ausencias, 'num_ausencias_ultima_sesion': num_ausencias_ultima_sesion})
        elif request.user.is_superuser:
            return render(request, 'index/index_admin.html')
        else:
            return render(request, 'index/index_cat.html')
    else:
        return render(request, 'index/index.html')

def c403(request):
    return render(request, '403.html', status=403)

def c404(request):
    return render(request, '404.html', status=404)

def c500(request):
    return render(request, '500.html', status=500)

def error(request, mensaje):
    return render(request, 'error.html', {'mensaje': mensaje})