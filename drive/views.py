from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FileForm, FolderForm
from .models import File, Folder
# Create your views here.

@login_required
def subir_archivo(request, folder_id=None):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            new_file = form.save(commit=False)
            new_file.owner = request.user
            new_file.name = file.name
            if folder_id is not None:
                folder = get_object_or_404(Folder,id=folder_id)
                new_file.parent_folder = folder
            new_file.save()
            if folder_id is not None:
                return redirect('listar_archivos_en_carpeta', folder_id)
            else:   
                return redirect('listar_archivos')
    else:
        form = FileForm()
    return render(request, 'subir_archivo.html', {'form': form})

@login_required
def listar_archivos(request, folder_id=None):
    ruta = []
    if folder_id is None:
        files = File.objects.filter(parent_folder=None)
        folders = Folder.objects.filter(parent_folder=None)
    else:
        folder = get_object_or_404(Folder,id=folder_id)
        files = File.objects.filter(parent_folder=folder)
        folders = Folder.objects.filter(parent_folder=folder)
        ruta = obtener_ruta_carpeta(folder) 
        print(ruta)
    return render(request, 'listar_archivos.html', {'files': files, 'folders':folders, 'actual_folder':folder_id, 'ruta':ruta})


@login_required
def crear_carpeta(request, folder_id=None):
    print(request.method)
    if request.method == 'POST':

        form = FolderForm(request.POST)
        if form.is_valid():
            new_folder = form.save(commit=False)
            new_folder.owner = request.user
            if folder_id is not None:
                folder = get_object_or_404(Folder,id=folder_id)
                new_folder.parent_folder = folder
            new_folder.save()
            if folder_id is not None:
                return redirect('listar_archivos_en_carpeta', folder_id)
            else:   
                return redirect('listar_archivos')
    else:
        form = FolderForm()
    return render(request, 'crear_carpeta.html', {'form': form})

def obtener_ruta_carpeta(carpeta):
    if carpeta.parent_folder is None:
        return [carpeta]
    else:
        return obtener_ruta_carpeta(carpeta.parent_folder) + [carpeta]