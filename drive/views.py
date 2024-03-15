from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FileForm
from .models import File
from django.core.validators import FileExtensionValidator
# Create your views here.

@login_required
def subir_archivo(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            new_file = form.save(commit=False)
            new_file.owner = request.user
            new_file.name = file.name
            new_file.save()
            print(new_file.is_image())
            return redirect('/')
    else:
        form = FileForm()
    return render(request, 'subir_archivo.html', {'form': form})

@login_required
def listar_archivos(request):
    files = File.objects.all()
    return render(request, 'listar_archivos.html', {'files': files})