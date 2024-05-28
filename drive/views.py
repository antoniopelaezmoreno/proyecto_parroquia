from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FolderForm, MoveFileForm, MoveFolderForm
from .models import Archivo, Carpeta
from django.http import JsonResponse
from django.db.models import Q
# Create your views here.

@login_required
def subir_archivo(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        id_carpeta_actual = request.POST.get('carpeta_actual')
        carpeta_actual = None
        if id_carpeta_actual is not None and id_carpeta_actual != 'None':
            carpeta_actual = get_object_or_404(Carpeta, id=id_carpeta_actual)
        nuevo_archivo = Archivo(file=archivo, owner=request.user, name=archivo.name, parent_folder=carpeta_actual)
        nuevo_archivo.save()
        return JsonResponse({'success': True})
    return redirect('listar_archivos')

@login_required
def listar_archivos(request, folder_id=None):
    ruta = []
    if folder_id is None:
        files = Archivo.objects.filter(parent_folder=None).order_by('id')
        folders = Carpeta.objects.filter(parent_folder=None).order_by('id')
    else:
        folder = get_object_or_404(Carpeta,id=folder_id)
        files = Archivo.objects.filter(parent_folder=folder).order_by('id')
        folders = Carpeta.objects.filter(parent_folder=folder).order_by('id')
        ruta = obtener_ruta_carpeta(folder) 
    return render(request, 'listar_archivos.html', {'files': files, 'folders':folders, 'actual_folder':folder_id, 'ruta':ruta})


@login_required
def crear_carpeta(request):
    if request.method == 'POST':
        nombre = request.POST.get('name')
        id_carpeta_actual = request.POST.get('carpeta_actual')
        carpeta_actual = None
        if id_carpeta_actual is not None and id_carpeta_actual != 'None':
            carpeta_actual = get_object_or_404(Carpeta, id=id_carpeta_actual)
        nueva_carpeta = Carpeta(name=nombre, owner=request.user, parent_folder=carpeta_actual)
        nueva_carpeta.save()
        return JsonResponse({'success': True})
    return redirect('listar_archivos')

def obtener_ruta_carpeta(carpeta):
    if carpeta.parent_folder is None:
        return [carpeta]
    else:
        return obtener_ruta_carpeta(carpeta.parent_folder) + [carpeta]
    
@login_required
def eliminar_archivo(request, file_id):
    file = get_object_or_404(Archivo, id=file_id)
    file.delete()
    return redirect('listar_archivos')

@login_required
def eliminar_carpeta(request, folder_id):
    folder = get_object_or_404(Carpeta, id=folder_id)
    folder.delete()
    return redirect('listar_archivos')

@login_required
def mover_archivo(request, file_id):
    file = get_object_or_404(Archivo, id=file_id)
    if request.method == 'POST':
        form = MoveFileForm(request.POST)
        if form.is_valid():
            folder = form.cleaned_data['parent_folder']
            file.parent_folder = folder
            file.save()
            return redirect('listar_archivos')
    else:
        form = MoveFileForm()
    return render(request, 'mover_archivo.html', {'form': form, 'file_id': file_id})



@login_required
def mover_carpeta(request, folder_id):
    folder = get_object_or_404(Carpeta, id=folder_id)
    if request.method == 'POST':
        form = MoveFolderForm(request.POST, current_folder=folder)
        if form.is_valid():
            print("valido")
            parent_folder = form.cleaned_data['parent_folder']
            if parent_folder != folder:
                folder.parent_folder = parent_folder
                folder.save()
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            print("no valido")
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = MoveFolderForm(current_folder=folder)
    return render(request, 'mover_carpeta.html', {'form': form, 'folder': folder})

@login_required
def obtener_carpetas_destino_carpeta(request, folder_id):
    folder = Carpeta.objects.get(id=folder_id)
    subfolders = folder.get_descendants()
    available_folders = list(Carpeta.objects.exclude(
        Q(id__in=[subfolder.id for subfolder in subfolders]) |
        Q(id=folder_id)
    ).values("id", "name"))
    
    data = {"available_folders": available_folders}
    return JsonResponse(data)

@login_required
def obtener_carpetas_destino_archivo(request):
    available_folders = list(Carpeta.objects.all().values("id", "name"))
    data = {"available_folders": available_folders}
    return JsonResponse(data)

@login_required
def cambiar_nombre_carpeta(request, folder_id):
    folder = get_object_or_404(Carpeta, id=folder_id)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = FolderForm(instance=folder)
    return render(request, 'cambiar_nombre_carpeta.html', {'form': form, 'folder': folder})
