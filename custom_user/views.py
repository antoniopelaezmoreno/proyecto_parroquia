from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import CustomUser
from solicitud_catequista.models import SolicitudCatequista
from .forms import CustomUserForm, EditCustomUserForm
from google_auth_oauthlib.flow import InstalledAppFlow
from django.contrib.auth.decorators import login_required
import json
from catecumeno.models import Catecumeno

def cerrar_sesion(request):
    logout(request)
    return redirect('/')


@login_required
def listar_catequistas(request):
    if request.user.is_superuser:
        catequistas = CustomUser.objects.all().exclude(is_superuser=True)
        return render(request, 'listar_catequistas_admin.html', {'catequistas': catequistas})
    elif request.user.is_coord:
        ciclo=request.user.ciclo
        catequistas = CustomUser.objects.filter(ciclo=ciclo)
        return render(request, 'listar_catequistas.html', {'catequistas': catequistas})
    else:
        return redirect('/403')

@login_required
def editar_catequista(request, id):
    catequista = get_object_or_404(CustomUser, id=id)
    if request.user.id == id:
        if request.method == 'POST':
            form = EditCustomUserForm(request.POST, instance=catequista)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = EditCustomUserForm(instance=catequista)
    else:
        return redirect('/403')
    return render(request, 'editar_catequista.html', {'form': form})
    
def crear_usuario_desde_solicitud(request, token):
    solicitud = get_object_or_404(SolicitudCatequista, token=token)

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            ciclo = solicitud.ciclo_asignado

            opcion_ciclo = Catecumeno.CicloChoices(ciclo)
            if opcion_ciclo is None:
                return redirect('/404')
            custom_user = form.save(commit=False)
            custom_user.nombre = solicitud.nombre
            custom_user.apellidos = solicitud.apellidos
            custom_user.email = solicitud.email
            custom_user.ciclo = opcion_ciclo
            custom_user.save()
            
            solicitud.delete()
            
            return redirect('/user/login')
    else:
        form = CustomUserForm()
    
    return render(request, 'crear_usuario_desde_solicitud.html', {'form': form})

@login_required
def convertir_a_coordinador(request):
    if request.method == 'POST':
        for ciclo in request.POST:
            if ciclo.startswith('cycle_'):

                cic = ciclo.split('cycle_')[1]
                user_id = request.POST[ciclo]

                if user_id:
                    todos_users = CustomUser.objects.filter(ciclo=cic)
                    todos_users.update(is_coord=False)
                    user = get_object_or_404(CustomUser, pk=user_id)
                    user.is_coord = True
                    user.save()

        return redirect('/')

    ciclos = [('posco_1','Posco 1'),('posco_2','Posco 2'),('posco_3','Posco 3'),('posco_4','Posco 4'),('gr_juv_1','Grupos Juveniles 1'),('gr_juv_2','Grupos Juveniles 2'),('catecumenados_1','Catecumenados 1'),('catecumenados_2','Catecumenados 2'),('catecumenados_3','Catecumenados 3')]


    usuarios_por_ciclo = {}
    for cycle in ciclos:
        usuarios_de_ciclo = CustomUser.objects.filter(ciclo=cycle[0])
        usuarios_por_ciclo[cycle] = usuarios_de_ciclo

    return render(request, 'crear_coordinadores.html', {'users_by_cycle': usuarios_por_ciclo})
