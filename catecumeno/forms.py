from django import forms
from .models import Catecumeno


class CatecumenoForm(forms.ModelForm):
    class Meta:
        model = Catecumeno
        fields = ['nombre', 'apellidos', 'email', 'dni','telefono','ciclo', 'nombre_madre', 'apellidos_madre', 'email_madre', 'telefono_madre', 'nombre_padre', 'apellidos_padre', 'email_padre', 'telefono_padre', 'preferencias', 'foto']


class CatecumenoEditForm(forms.ModelForm):
    class Meta:
        model = Catecumeno
        fields = ['nombre', 'apellidos', 'email', 'dni','telefono','ciclo', 'nombre_madre', 'apellidos_madre', 'email_madre', 'telefono_madre', 'nombre_padre', 'apellidos_padre', 'email_padre', 'telefono_padre', 'foto']

