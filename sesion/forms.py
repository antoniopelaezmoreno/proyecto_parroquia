from django import forms
from .models import Sesion
from drive.models import File

class SesionForm(forms.ModelForm):
    files = forms.ModelMultipleChoiceField(queryset=File.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = Sesion
        fields = ['titulo', 'descripcion', 'fecha', 'files']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }