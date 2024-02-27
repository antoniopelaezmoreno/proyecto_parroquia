from django.shortcuts import render, redirect
from .forms import CatecumenoForm
from .models import Catecumeno


def crear_catecumeno(request):
    if request.method == 'POST':
        form = CatecumenoForm(request.POST, request.FILES)
        if form.is_valid():
            catecumeno = form.save()
            return redirect('/')
    else:
        form = CatecumenoForm()
    
    return render(request, 'crear_catecumeno.html', {'form': form})

def listar_catecumenos(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            catecumenos = Catecumeno.objects.all()
            return render(request, 'listar_catecumenos_admin.html', {'catecumenos': catecumenos})
        elif request.user.is_coord:
            ciclo=request.user.ciclo
            catecumenos = Catecumeno.objects.filter(ciclo=ciclo)
            return render(request, 'listar_catecumenos.html', {'catecumenos': catecumenos})
        else:
            return redirect('/403')
    else:
            return redirect('/403')
    



