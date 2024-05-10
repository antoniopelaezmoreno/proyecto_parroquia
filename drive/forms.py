from django import forms
from .models import File, Folder
from django.db.models import Q

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class MoveFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['parent_folder']

class MoveFolderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        current_folder = kwargs.pop('current_folder', None)
        super().__init__(*args, **kwargs)
        if current_folder:
            # Obtener todas las subcarpetas de la carpeta actual
            subfolders = current_folder.get_descendants()
            # Excluir las subcarpetas del queryset del campo parent_folder
            self.fields['parent_folder'].queryset = Folder.objects.exclude(
                Q(id__in=[subfolder.id for subfolder in subfolders]) |
                Q(id=current_folder.id)
            )
        self.fields['parent_folder'].empty_label = 'Principal'

    class Meta:
        model = Folder
        fields = ['parent_folder']