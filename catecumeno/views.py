from django.shortcuts import render, redirect
from .forms import CatecumenoForm

def crear_catecumeno(request):
    if request.method == 'POST':
        form = CatecumenoForm(request.POST, request.FILES)
        if form.is_valid():
            catecumeno = form.save()
            return redirect('/')
    else:
        form = CatecumenoForm()
    
    return render(request, 'crear_catecumeno.html', {'form': form})
