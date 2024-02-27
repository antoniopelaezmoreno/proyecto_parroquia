from django.shortcuts import render, redirect
from .forms import SesionForm
from .models import Catecumeno
from django.utils import timezone
from django.contrib import messages
# Create your views here.

def crear_sesion(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/sesion/crear/posco_1')
        ciclo=request.user.ciclo
        if request.method == 'POST':
            form = SesionForm(request.POST, request.FILES)
            if form.is_valid():
                fecha = form.cleaned_data['fecha']
                if fecha > timezone.now().date():
                    sesion = form.save(commit=False)
                    sesion.ciclo = ciclo
                    sesion.save()
                    return redirect('/')
                else:
                    messages.error(request, "La fecha no puede estar en el pasado")
            else:
                messages.error(request, "La fecha no puede estar en el pasado")
        else:
            form = SesionForm()
        return render(request, 'crear_sesion.html', {'form': form, 'ciclo': ciclo})
    else:
        return redirect('/403')
    
def crear_sesion_admin(request, ciclo):
    if request.user.is_superuser:
        valores_ciclo = [choice[0] for choice in Catecumeno.CicloChoices.choices]
        if ciclo not in valores_ciclo:
            return redirect('/404')
        if request.method == 'POST':
            form = SesionForm(request.POST, request.FILES)
            if form.is_valid():
                fecha = form.cleaned_data['fecha']
                if fecha > timezone.now().date():
                    sesion = form.save(commit=False)
                    sesion.ciclo = ciclo
                    sesion.save()
                    return redirect('/')
                else:
                    messages.error(request, "La fecha no puede estar en el pasado")
            else:
                messages.error(request, "Introduzca todos los campos correctamente")
        else:
            form = SesionForm()
        return render(request, 'crear_sesion.html', {'form': form, 'ciclo': ciclo})
    else:
        return redirect('/403')