from django import forms
from .models import Archivo, Carpeta
from django.db.models import Q

class FileForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['file']

class FolderForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ['name']

class MoveFileForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['parent_folder']

class MoveFolderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_folder = kwargs.pop('current_folder', None)
        super().__init__(*args, **kwargs)
        if current_folder:
            # Obtener todas las subcarpetas de la carpeta actual
            subfolders = current_folder.get_descendants()
            # Excluir las subcarpetas del queryset del campo parent_folder
            self.fields['parent_folder'].queryset = Carpeta.objects.exclude(
                Q(id__in=[subfolder.id for subfolder in subfolders]) |
                Q(id=current_folder.id)
            )
        self.fields['parent_folder'].empty_label = 'Principal'

    class Meta:
        model = Carpeta
        fields = ['parent_folder']