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