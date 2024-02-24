from django import forms
from .models import Catecumeno

class CatecumenoForm(forms.ModelForm):
    class Meta:
        model = Catecumeno
        fields = ['nombre', 'apellidos', 'email', 'dni','ciclo', 'nombre_madre', 'apellidos_madre', 'email_madre', 'dni_madre', 'nombre_padre', 'apellidos_padre', 'email_padre', 'dni_padre', 'preferencias', 'foto']
