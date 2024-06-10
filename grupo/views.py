from django.shortcuts import render, redirect, get_object_or_404
from .forms import GrupoForm
from django.http import JsonResponse
from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
from sesion.models import Sesion
from .models import Grupo
from curso.models import Curso
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Create your views here.

@login_required
def crear_grupo(request):
    ciclo = request.user.ciclo
    if request.user.is_superuser:
        ciclo = request.GET.get('ciclo')
        if ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
            return redirect('/404')
    if request.user.is_coord or request.user.is_superuser:
        grupo = Grupo.objects.create(ciclo=ciclo)
        grupo.save()
        return redirect('/grupo?ciclo=' + ciclo)
    
    else:
        return redirect('/403')
        
@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, pk=grupo_id)
    if request.user.ciclo == grupo.ciclo or request.user.is_superuser:
        catequistas = CustomUser.objects.filter(ciclo=grupo.ciclo)
        if request.method == 'POST':
            form = GrupoForm(request.POST, request.FILES, instance=grupo, catequistas=catequistas)
            if form.is_valid():
                grupo = form.save(commit=False)
                grupo.save()
                return redirect('/grupo?ciclo='+grupo.ciclo)
            else:
                errores = form.errors['__all__'][0]
                request.session['errores'] = [grupo.id,errores]
                return redirect('/grupo?ciclo='+grupo.ciclo)
        else:
            return redirect('/404')
                
    else:
        return redirect('/403')
    
@login_required
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, pk=grupo_id)
    if request.user.ciclo == grupo.ciclo or request.user.is_superuser:
        grupo.delete()
        return redirect('/grupo?ciclo='+grupo.ciclo)
    else:
        return redirect('/403')
    
@login_required
def crear_grupo_admin(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            ciclo = request.POST.get('ciclo')
            catequista1_id = request.POST.get('catequista1')
            catequista2_id = request.POST.get('catequista2')

            catequista1 = CustomUser.objects.get(id=catequista1_id)
            catequista2 = CustomUser.objects.get(id=catequista2_id)

            if Grupo.objects.filter(ciclo=catequista1.ciclo, catequista1=catequista1).exists() or Grupo.objects.filter(ciclo=catequista1.ciclo, catequista2=catequista1).exists():
                error =  ValidationError("El catequista 1 ya está en otro grupo del mismo ciclo.")
                return render(request, 'crear_grupo_admin.html', {'error': error.message})
            if Grupo.objects.filter(ciclo=catequista2.ciclo, catequista2=catequista2).exists() or Grupo.objects.filter(ciclo=catequista2.ciclo, catequista1=catequista2).exists():
                error =  ValidationError("El catequista 2 ya está en otro grupo del mismo ciclo.")
                return render(request, 'crear_grupo_admin.html', {'error': error.message})
            
            grupo = Grupo.objects.create(
                ciclo=ciclo,
                catequista1=catequista1,
                catequista2=catequista2,
            )
                
            return redirect('/') 
        else:
            return render(request, 'crear_grupo_admin.html')
    else:
       return redirect('/403')

@login_required
def ajax_obtener_catequistas(request):
    ciclo_id = request.GET.get('ciclo_id')
    catequistas = CustomUser.objects.filter(ciclo=ciclo_id)
    catequistas_data = [{'id': catequista.id, 'nombre': catequista.nombre, 'apellidos': catequista.apellidos} for catequista in catequistas]
    return JsonResponse({'catequistas': catequistas_data})

@login_required
def panel_grupos(request):
    from core.views import error
    ciclo=request.user.ciclo
    if request.user.is_superuser:
        ciclo = request.GET.get('ciclo')
        if ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
            return redirect('/404')
    mensaje_error = request.session.pop('errores', "")
    sesiones = Sesion.objects.filter(ciclo=ciclo, curso=Curso.objects.latest('id')).order_by('fecha')
    if request.user.is_coord or request.user.is_superuser:
        catequistas = CustomUser.objects.filter(ciclo=ciclo)
        grupos = Grupo.objects.filter(ciclo=ciclo)
        return render(request, 'panel_grupos_coord.html', {'grupos': grupos, 'catequistas': catequistas, 'error': mensaje_error, 'sesiones': sesiones, 'ciclo': ciclo})
    else:
        grupo1 = Grupo.objects.filter(catequista1=request.user).first()
        grupo2 = Grupo.objects.filter(catequista2=request.user).first()
        if grupo1:
            catequistas = [grupo1.catequista1, grupo1.catequista2]
            grupos = [grupo1]
        elif grupo2:
            catequistas = [grupo2.catequista1, grupo2.catequista2]
            grupos = [grupo2]
        else:
            return error(request, 'No tienes grupo asignado')
        return render(request, 'panel_grupos_catequista.html', {'grupos': grupos, 'catequistas': catequistas, 'error': mensaje_error, 'sesiones': sesiones, 'ciclo': ciclo})

@login_required
def generar_grupos_aleatorios(request):
    ciclo = request.user.ciclo
    if not request.user.is_superuser and not request.user.is_coord:
        return redirect('/403')
    if request.user.is_superuser:
        ciclo = request.GET.get('ciclo')
        if ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
            return redirect('/404')
    catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
    grupos_ciclo = Grupo.objects.filter(ciclo=ciclo)
    n_grupos = grupos_ciclo.count()
    if n_grupos == 0:
        return redirect(reverse('panel_grupos') + f'?ciclo={ciclo}')

    max_miembros_grupo = catecumenos.count() / n_grupos + 3

    prob = LpProblem("Asignación de catecúmenos a grupos", LpMaximize)

    # Definir las variables de decisión
    x = LpVariable.dicts("Asignación", [(c.id, g.id) for c in catecumenos for g in grupos_ciclo], cat='Binary')

    # Definir la función objetivo
    prob += lpSum([x[(c.id, g.id)] for c in catecumenos for g in grupos_ciclo])

    # Definir las restricciones
    for c in catecumenos:
        prob += sum(x[(c.id, g.id)] for g in grupos_ciclo) == 1  # Cada catecúmeno debe estar en un solo grupo
    for g in grupos_ciclo:
        prob += sum(x[(c.id, g.id)] for c in catecumenos) <= max_miembros_grupo # Número máximo de catecúmenos por grupo

    prob.solve()

    for c in catecumenos:
        for g in grupos_ciclo:
            if x[(c.id, g.id)].value() == 1:
                c.grupo = g
                c.save()

    return redirect(reverse('panel_grupos') + f'?ciclo={ciclo}')