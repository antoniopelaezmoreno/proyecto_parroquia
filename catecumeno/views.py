from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .forms import CatecumenoForm, CatecumenoEditForm
from .models import Catecumeno
from grupo.models import Grupo
from sesion.models import Sesion
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def crear_catecumeno(request):
    logout(request)
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
def asociar_preferencias(request):
    ciclo = request.user.ciclo
    if request.user.is_superuser:
        ciclo = request.GET.get('ciclo')
        if ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
            return redirect('/404')

    if request.user.is_coord or request.user.is_superuser:
        usuarios_disponibles = Catecumeno.objects.filter(ciclo=ciclo)

        if request.method == 'POST':
            for alumno in usuarios_disponibles:
                usuarios_asociados_ids = request.POST.getlist(f'usuarios-{alumno.id}')
                lista_alumnos_preferidos = []
                for usuario_asociado_id in usuarios_asociados_ids:
                    lista_alumnos_preferidos.append(Catecumeno.objects.get(id=usuario_asociado_id))
                alumno.preferencias_procesadas.set(lista_alumnos_preferidos)
                alumno.save()

        context = {'alumnos_con_preferencias': usuarios_disponibles, 'usuarios_disponibles': usuarios_disponibles, 'ciclo': ciclo}
        return render(request, 'asociar_preferencias.html', context)
    else:
        return redirect('/403')

@login_required
@csrf_exempt
def asignar_catecumenos_a_grupo(request):
    ciclo = request.user.ciclo
    if request.user.is_superuser:
        ciclo = request.GET.get('ciclo')
        if ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
            return redirect('/404')

    if request.user.is_coord or request.user.is_superuser:
        grupos = Grupo.objects.filter(ciclo=ciclo)
        if request.method == 'POST':
            data = json.loads(request.body)
            for grupo in grupos:
                grupo.miembros.clear()
                grupo.save()
            for asignacion in data:
                catecumeno_id = asignacion.get('userId')
                grupo_asignado = asignacion.get('grupoAsignado')
                if grupo_asignado:
                    catecumeno = Catecumeno.objects.get(id=catecumeno_id)
                    grupo = Grupo.objects.get(id=grupo_asignado)
                    grupo.miembros.add(catecumeno)
                    grupo.save()
            return redirect('index')
        catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
        return render(request, 'asignar_catecumenos_a_grupo.html', {'catecumenos': catecumenos, 'grupos': grupos, 'ciclo': ciclo})
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
        previous_page = request.META.get('HTTP_REFERER', '/')
        if request.user.is_superuser:
            catecumeno.delete()
            if previous_page.endswith(f'/catecumeno/{id}/'):
                return redirect('/')
            else:
                return redirect(previous_page)
        elif request.user.is_coord and catecumeno.ciclo == request.user.ciclo:
            catecumeno.delete()
            if previous_page.endswith(f'/catecumeno/{id}/'):
                return redirect('/')
            else:
                return redirect(previous_page)
        else:
            return redirect('/403')
    else:
        return redirect('/403')
    
@login_required
def mostrar_catecumeno(request, id):
    catecumeno = get_object_or_404(Catecumeno,id=id)
    catequistas = obtener_catequistas_de_catecumeno(catecumeno)
    ausencias, justificaciones, asistencias = contar_ausencias_justificaciones_asistencias(request, id)
    if request.user.is_superuser or (request.user.is_coord and catecumeno.ciclo == request.user.ciclo):
        return render(request, 'mostrar_catecumeno.html', {'catecumeno': catecumeno, 'catequistas': catequistas, 'ausencias': ausencias, 'justificaciones': justificaciones, 'asistencias': asistencias})
    else:
        return redirect('/403')
    

@login_required
def contar_ausencias_justificaciones_asistencias(request, catecumeno_id):
    catecumeno = get_object_or_404(Catecumeno, id=catecumeno_id)
    ausencias = Sesion.objects.filter(ciclo=catecumeno.ciclo).filter(ausentes=catecumeno)
    justificaciones = Sesion.objects.filter(ciclo=catecumeno.ciclo).filter(justificados=catecumeno)
    asistencias = Sesion.objects.filter(ciclo=catecumeno.ciclo).filter(asistentes=catecumeno)
    return ausencias, justificaciones, asistencias
    
@login_required
def editar_catecumeno(request, id):
    catecumeno = get_object_or_404(Catecumeno,id=id)
    catequistas = obtener_catequistas_de_catecumeno(catecumeno)
    ausencias, justificaciones, asistencias = contar_ausencias_justificaciones_asistencias(request, id)
    if request.user.is_superuser or (request.user.is_coord and catecumeno.ciclo == request.user.ciclo):
        if request.method == 'POST':
            form = CatecumenoEditForm(request.POST, request.FILES, instance=catecumeno)
            if form.is_valid():
                form.save()
                return redirect('mostrar_catecumeno', id=id)
            else:
                print(form.errors)
        else:
            form = CatecumenoEditForm(instance=catecumeno)
        return render(request, 'editar_catecumeno.html', {'form': form, 'catecumeno': catecumeno, 'catequistas': catequistas, 'ausencias': ausencias, 'justificaciones': justificaciones, 'asistencias': asistencias})
    else:
        return redirect('/403')
    
def obtener_catequistas_de_catecumeno(catecumeno):
    grupos = Grupo.objects.filter(ciclo=catecumeno.ciclo)
    catequistas = []
    for grupo in grupos:
        if catecumeno in grupo.miembros.all():
            catequistas.append(grupo.catequista1.first_name)
            catequistas.append(grupo.catequista2.first_name)
    return catequistas
