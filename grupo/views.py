from django.shortcuts import render, redirect
from .forms import GrupoForm

from custom_user.models import CustomUser
from catecumeno.models import Catecumeno


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
            return render(request, '403.html')
    else:
        return render(request, '403.html')
    
def crear_grupo_admin(request, ciclo):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            valores_ciclo = [choice[0] for choice in Catecumeno.CicloChoices.choices]
            if ciclo not in valores_ciclo:
                return render(request, '404.html')
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
            return render(request, '403.html')
    else:
        return render(request, '403.html')