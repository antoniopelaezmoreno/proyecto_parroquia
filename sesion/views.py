from django.shortcuts import render, redirect
from .forms import SesionForm
from .models import Catecumeno
from django.utils import timezone
from django.contrib import messages
from .models import Sesion
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
