from django import forms
from .models import Sesion

class SesionForm(forms.ModelForm):
    class Meta:
        model = Sesion
        fields = ['titulo', 'descripcion', 'fecha']
        widgets = {
                'fecha': forms.DateInput(attrs={'type': 'date'})
            }