from http.client import HTTPResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GrupoForm
from django.http import JsonResponse
from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
from sesion.models import Sesion
from .models import Grupo
from curso.models import Curso
import random
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages

# Create your views here.

@login_required
def crear_grupo(request):
    if request.user.is_authenticated:
        if request.user.is_coord:
            ciclo = request.user.ciclo
            grupo = Grupo.objects.create(ciclo=ciclo)
            grupo.save()
            return redirect('/grupo')
        if request.user.is_superuser:
            return redirect('crear_grupo_admin')
        else:
            return redirect('/403')
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
                return redirect('/grupo')
            else:
                errores = form.errors['__all__'][0]
                request.session['errores'] = [grupo.id,errores]
                return redirect('/grupo')
                
        else:
            form = GrupoForm(instance=grupo, catequistas=catequistas)
        return render(request, 'editar_grupo.html', {'form': form})
    else:
        return redirect('/403')
    
@login_required
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, pk=grupo_id)
    if request.user.ciclo == grupo.ciclo or request.user.is_superuser:
        grupo.delete()
        return redirect('/grupo')
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
                curso= Curso.objects.latest('id')
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
    catequistas_data = [{'id': catequista.id, 'first_name': catequista.first_name, 'last_name': catequista.last_name} for catequista in catequistas]
    return JsonResponse({'catequistas': catequistas_data})

@login_required
def panel_grupos(request):
    if request.user.is_coord:
        error = request.session.pop('errores', "")
        catequistas = CustomUser.objects.filter(ciclo=request.user.ciclo)
        grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
        sesiones = Sesion.objects.filter(ciclo=request.user.ciclo, curso=Curso.objects.latest('id')).order_by('fecha')
        return render(request, 'panel_grupos_coord.html', {'grupos': grupos, 'catequistas': catequistas, 'error': error, 'sesiones': sesiones})

''' 
def calcular_valor(grupos, lista_catecumenos, num_grupos, preferencias_totales):
   
    num_miembros_grupo = {}
    preferencias = {}

    for catecumeno in lista_catecumenos:
        preferencias[catecumeno] = set(catecumeno.preferencias_procesadas.all())

    numero_preferencias_cumplidas = 0
    for i, catecumeno in enumerate(lista_catecumenos):
        grupo_actual = grupos[i]
        for otra_catecumeno in lista_catecumenos[i + 1:]:
            if grupos[i] == grupos[i + 1:]:
                if otra_catecumeno in preferencias[catecumeno]:
                    numero_preferencias_cumplidas += 1

        if grupo_actual not in num_miembros_grupo:
            num_miembros_grupo[grupo_actual] = 1
        else:
            num_miembros_grupo[grupo_actual] += 1

    num_keys = len(num_miembros_grupo.keys())
    castigo=0
    if num_keys < num_grupos:
        castigo=1
    
    if num_miembros_grupo:
        max_miembros = max(num_miembros_grupo.values())
        min_miembros = min(num_miembros_grupo.values())
        diferencia = max_miembros - min_miembros
    else:
        diferencia = 0

    print("Preferencias cumplidas: ", numero_preferencias_cumplidas)
    print(numero_preferencias_cumplidas/preferencias_totales)
    valor = numero_preferencias_cumplidas/preferencias_totales - diferencia *50 - castigo * 10
    #print(valor)
    return valor
'''
def calcular_valor(grupos, lista_catecumenos, num_grupos, preferencias_totales):
    contador_preferencias = 0
    map = {}

    for grupo in grupos:
        map[grupo] = map.get(grupo, 0) + 1
    
    min_value = min(map.values())
    max_value = max(map.values())
    num_keys = len(map.keys())
    castigo=0
    if num_keys < num_grupos:
        castigo=1
    
    diff = max_value - min_value
    
    for i in range(len(grupos)):
        for j in range(i + 1, len(grupos)):
            if grupos[i] == grupos[j] and lista_catecumenos[j] in lista_catecumenos[i].preferencias_procesadas.all():
                contador_preferencias += 1
    #print("Preferencias cumplidas: ", contador_preferencias)
    return contador_preferencias - diff * 100 - castigo * 1000

def fitness(grupos, lista_catecumenos,num_grupos):
    contador_preferencias = 0
    map = {}

    for grupo in grupos:
        map[grupo] = map.get(grupo, 0) + 1
    
    min_value = min(map.values())
    max_value = max(map.values())
    num_keys = len(map.keys())
    castigo=0
    if num_keys < num_grupos:
        castigo=1
    
    diff = max_value - min_value
    
    for i in range(len(grupos)):
        for j in range(i + 1, len(grupos)):
            if grupos[i] == grupos[j] and lista_catecumenos[j] in lista_catecumenos[i].preferencias_procesadas.all():
                contador_preferencias += 1
    
    return contador_preferencias - diff * 100 - castigo * 1000


def ag(request):
    catecumenos = Catecumeno.objects.filter(ciclo='catecumenados_1')
    preferencias_totales = 0
    for catecumeno in catecumenos:
        preferencias_totales += len(catecumeno.preferencias_procesadas.all())
    print(preferencias_totales)
    num_grupos=4
    num_catecumenos=len(catecumenos)
    solutions=[]
    for s in range(20):
        lista = [random.randint(1, num_grupos) for _ in range(num_catecumenos)]
        solutions.append(lista)
    
    for i in range(20):
        print("Generacion ", i+1)
        rankedsolutions=[]
        for s in solutions:
            fit=calcular_valor(s, catecumenos, num_grupos, preferencias_totales)
            rankedsolutions.append((fit,s))
        rankedsolutions.sort(key=lambda x: x[0], reverse=True)
        print(rankedsolutions[:1])

        bestsolutions = rankedsolutions[:100]
        
        lista=[[] for _ in range(num_catecumenos)]
        for s in bestsolutions:
            for i in range(num_catecumenos):
                lista[i].append((s[1][i]))

        newGen=[]
        for s in range(20):
            newGen.append(tuple(random.choice(lista[l]) for l in range(num_catecumenos)))
        solutions = newGen
    print("Mejor solucion: ", bestsolutions[0])
    grupo_final=bestsolutions[0][1]

    map = {}
    for g in range(num_catecumenos):
        if grupo_final[g] not in map:
            map[grupo_final[g]] = [Catecumeno.objects.get(id=catecumenos[g].id)]
        else:
            map[grupo_final[g]].append(Catecumeno.objects.get(id=catecumenos[g].id))
        
    for key in map:
        print("Grupo ", key)
        for catecumeno in map[key]:
            print(catecumeno.nombre)
        print("-----------------")
        
    return redirect('/')
