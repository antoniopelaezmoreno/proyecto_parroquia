from django import forms
from .models import SolicitudCatequista

class SolicitudCatequistaForm(forms.ModelForm):
    class Meta:
        model = SolicitudCatequista
        fields = ['nombre','apellidos','email','disponibilidad','preferencias']
