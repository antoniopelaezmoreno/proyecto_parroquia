from django.shortcuts import render, redirect
from .models import Notificacion
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def ver_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user, visto=False)
    return notificaciones

@login_required
def marcar_notificacion_vista(request, notificacion_id):
    notificacion = Notificacion.objects.get(id=notificacion_id)
    if notificacion.destinatario == request.user:
        notificacion.visto = True
        notificacion.save()
        return redirect('/')
    else:
        return redirect('/403')

    
