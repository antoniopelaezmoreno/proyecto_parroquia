from django.shortcuts import render, redirect
from .forms import GrupoForm
from django.http import JsonResponse
from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
from .models import Grupo
from curso.models import Curso
import random
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def crear_grupo(request):
    if request.user.is_authenticated:
        if request.user.is_coord:
            ciclo = request.user.ciclo
            catequistas = CustomUser.objects.filter(ciclo=ciclo)
            if request.method == 'POST':
                form = GrupoForm(request.POST, request.FILES, catequistas=catequistas)
                if form.is_valid():
                    grupo = form.save(commit=False)
                    grupo.ciclo = ciclo
                    grupo.save()
                    return redirect('/')
            else:
                form = GrupoForm(catequistas=catequistas)
            return render(request, 'crear_grupo.html', {'form': form, 'ciclo': ciclo})
        if request.user.is_superuser:
            return redirect('/grupo/crear_grupo/posco_1')
        else:
            return redirect('/403')
    else:
        return redirect('/403')

@login_required
def crear_grupo_admin(request, ciclo):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            valores_ciclo = [choice[0] for choice in Catecumeno.CicloChoices.choices]
            if ciclo not in valores_ciclo:
                return redirect('/403')
            catequistas = CustomUser.objects.filter(ciclo=ciclo)
            if request.method == 'POST':
                form = GrupoForm(request.POST, request.FILES, catequistas=catequistas)
                if form.is_valid():
                    grupo = form.save(commit=False)
                    grupo.ciclo = ciclo
                    grupo.save()
                    return redirect('/')
            else:
                form = GrupoForm(catequistas=catequistas)
            return render(request, 'crear_grupo.html', {'form': form, 'ciclo': ciclo})
        else:
            return redirect('/403')
    else:
        return redirect('/403')
    
def obtener_miembros_de_grupos(request):
    if request.method == 'GET':
        ciclo = request.user.ciclo
        curso_actual = Curso.objects.latest('id')
        
        grupos = Grupo.objects.filter(ciclo=ciclo, curso=curso_actual).prefetch_related('miembros')

        miembros_de_grupos = {}
        for grupo in grupos:
            miembros_de_grupo = [miembro.nombre for miembro in grupo.miembros.all()] 
            miembros_de_grupos[grupo.id] = miembros_de_grupo
        
        return JsonResponse(miembros_de_grupos)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405) 

def calcular_valor(grupos, lista_catecumenos, num_grupos):
   
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

    valor = numero_preferencias_cumplidas - diferencia *10 - castigo * 10

    return valor

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
    num_grupos=4
    num_catecumenos=len(catecumenos)
    solutions=[]
    for s in range(20):
        lista = [random.randint(1, num_grupos) for _ in range(num_catecumenos)]
        solutions.append(lista)
    
    for i in range(20):
        rankedsolutions=[]
        for s in solutions:
            fit=calcular_valor(s, catecumenos, num_grupos)
            rankedsolutions.append((fit,s))
        rankedsolutions.sort(reverse=True)

        bestsolutions = rankedsolutions[:100]
        
        lista=[[] for _ in range(num_catecumenos)]
        for s in bestsolutions:
            for i in range(num_catecumenos):
                lista[i].append((s[1][i]))

        newGen=[]
        for s in range(20):
            newGen.append(tuple(random.choice(lista[l]) for l in range(num_catecumenos)))
        solutions = newGen
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
