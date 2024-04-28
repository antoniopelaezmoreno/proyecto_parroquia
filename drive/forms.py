from django import forms
from .models import File, Folder

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
            self.fields['parent_folder'].queryset = Folder.objects.exclude(id=current_folder.id)
        self.fields['parent_folder'].empty_label = 'Principal'

    class Meta:
        model = Folder
        fields = ['parent_folder']