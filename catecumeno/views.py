from django.shortcuts import render, redirect, get_object_or_404
from .forms import CatecumenoForm
from .models import Catecumeno
from grupo.models import Grupo
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def crear_catecumeno(request):
    if request.method == 'POST':
        form = CatecumenoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CatecumenoForm()
    
    return render(request, 'crear_catecumeno.html', {'form': form})

@login_required
def listar_catecumenos(request):
    if request.user.is_superuser:
        catecumenos = Catecumeno.objects.all()
        return render(request, 'listar_catecumenos_admin.html', {'catecumenos': catecumenos})
    elif request.user.is_coord:
        ciclo=request.user.ciclo
        catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
        return render(request, 'listar_catecumenos.html', {'catecumenos': catecumenos})
    else:
        return redirect('/403')
    
@login_required
def asociar_preferencias(request, ciclo):
    if request.user.is_coord and request.user.ciclo == ciclo:
        usuarios_disponibles = Catecumeno.objects.filter(ciclo=ciclo)

        if request.method == 'POST':
            for alumno in usuarios_disponibles:
                usuarios_asociados_ids = request.POST.getlist(f'usuarios-{alumno.id}')
                lista_alumnos_preferidos = []
                for usuario_asociado_id in usuarios_asociados_ids:
                    lista_alumnos_preferidos.append(Catecumeno.objects.get(id=usuario_asociado_id))
                alumno.preferencias_procesadas.set(lista_alumnos_preferidos)
                alumno.save()

        context = {'alumnos_con_preferencias': usuarios_disponibles, 'usuarios_disponibles': usuarios_disponibles, 'curso': ciclo}
        return render(request, 'asociar_preferencias.html', context)
    else:
        return redirect('/403')

@login_required
@csrf_exempt
def asignar_catecumenos_a_grupo(request):
    if request.user.is_coord:
        ciclo = request.user.ciclo
        grupos = Grupo.objects.filter(ciclo=ciclo)
        if request.method == 'POST':
            data = json.loads(request.body)
            for grupo in grupos:
                grupo.miembros.clear()
                grupo.save()
            for asignacion in data:
                catecumeno_id = asignacion.get('userId')
                grupo_asignado = asignacion.get('grupoAsignado')
                catecumeno = Catecumeno.objects.get(id=catecumeno_id)
                grupo = Grupo.objects.get(id=grupo_asignado)
                grupo.miembros.add(catecumeno)
                grupo.save()
            return redirect('index')
        catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
        return render(request, 'asignar_catecumenos_a_grupo.html', {'catecumenos': catecumenos, 'grupos': grupos})
    else:
        return redirect('/403')

@login_required
def ver_autorizaciones(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            catecumenos = Catecumeno.objects.all()
            return render(request, 'ver_autorizaciones.html', {'catecumenos': catecumenos})
        elif request.user.is_coord:
            ciclo=request.user.ciclo
            catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
            return render(request, 'ver_autorizaciones.html', {'catecumenos': catecumenos})
        else:
            return redirect('/403')
    else:
        return redirect('/403')
    
@login_required
def eliminar_catecumeno(request, id):
    if request.user.is_authenticated:
        catecumeno = get_object_or_404(Catecumeno,id=id)
        if request.user.is_superuser:
            catecumeno.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif request.user.is_coord and catecumeno.ciclo == request.user.ciclo:
            catecumeno.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return redirect('/403')
    else:
        return redirect('/403')
    
@login_required
def mostrar_catecumeno(request, id):
    catecumeno = get_object_or_404(Catecumeno,id=id)
    if request.user.is_superuser:
        return render(request, 'mostrar_catecumeno.html', {'catecumeno': catecumeno})
    elif request.user.is_coord and catecumeno.ciclo == request.user.ciclo:
        return render(request, 'mostrar_catecumeno.html', {'catecumeno': catecumeno})
    else:
        return redirect('/403')