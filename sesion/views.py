from django.shortcuts import render, redirect, get_object_or_404
from .forms import SesionForm
from .models import Catecumeno
from django.utils import timezone
from django.contrib import messages
from .models import Sesion
from grupo.models import Grupo
# Create your views here.

def crear_sesion(request):
    if request.user.is_authenticated:
        ciclo=request.user.ciclo
        if request.user.is_superuser:
            ciclo = request.POST.get('ciclo')
        
        if request.method == 'POST':
            form = SesionForm(request.POST, request.FILES)
            if form.is_valid():
                fecha = form.cleaned_data['fecha']
                if fecha > timezone.now().date():
                    sesion = form.save(commit=False)
                    sesion.ciclo = ciclo
                    sesion.save()
                    return redirect('/sesion/listar')
                else:
                    messages.error(request, "La fecha no puede estar en el pasado")
            else:
                messages.error(request, "La fecha no puede estar en el pasado")
        else:
            form = SesionForm()
        return render(request, 'crear_sesion.html', {'form': form})
    else:
        return redirect('/403')
    
def listar_sesiones(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            sesiones = Sesion.objects.all()
            return render(request, 'listar_sesiones_admin.html', {'sesiones': sesiones})
        else:
            ciclo=request.user.ciclo
            sesiones = Sesion.objects.filter(ciclo=ciclo)
            return render(request, 'listar_sesiones.html', {'sesiones': sesiones})
    else:
        return redirect('/403')
    
def pasar_lista(request, sesionid):
    if request.user.is_authenticated:
        sesion = get_object_or_404(Sesion, pk=sesionid)
        if request.user.ciclo == sesion.ciclo:
            if request.method == 'POST':
                asistentes = request.POST.getlist('asistentes')
                justificados = request.POST.getlist('justificados')
                ausentes = request.POST.getlist('ausentes')
                sesion.asistentes.set(asistentes)
                sesion.justificados.set(justificados)
                sesion.ausentes.set(ausentes)
                sesion.save()
                return redirect('/sesion/listar')
            else:
                catecumenos = catecumenos_desde_catequista(request.user)
                return render(request, 'pasar_lista.html', {'sesion': sesion, 'catecumenos': catecumenos})
        else:
            return redirect('/403')
    else:
        return redirect('/403')



def catecumenos_desde_catequista(catequista):
    grupo = get_object_or_404(Grupo,catequista1=catequista) or get_object_or_404(Grupo,catequista2=catequista)
    return grupo.miembros.all()
