from django.shortcuts import render, redirect
from .forms import GrupoForm
from django.http import JsonResponse
from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
from .models import Grupo
from curso.models import Curso


# Create your views here.
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
        
        # Obtener los grupos correspondientes al ciclo y curso
        grupos = Grupo.objects.filter(ciclo=ciclo, curso=curso_actual).prefetch_related('miembros')
        
        # Construir un diccionario con los miembros de cada grupo
        miembros_de_grupos = {}
        for grupo in grupos:
            miembros_de_grupo = [miembro.nombre for miembro in grupo.miembros.all()]  # Suponiendo que "nombre" es un campo en el modelo Catecumeno
            miembros_de_grupos[grupo.id] = miembros_de_grupo
        
        return JsonResponse(miembros_de_grupos)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405) 