from django.shortcuts import render, redirect
from .forms import SolicitudCatequistaForm

# Create your views here.
def crear_solicitud_cateqista(request):
    if request.method == 'POST':
        form = SolicitudCatequistaForm(request.POST, request.FILES)
        if form.is_valid():
            catecumeno = form.save()
            return redirect('/')  # Especifica la ruta a la que quieres redirigir después de crear el catecumeno
    else:
        form = SolicitudCatequistaForm()
    
    return render(request, 'crear_solicitud_catequista.html', {'form': form})