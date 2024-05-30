from django import forms
from .models import SolicitudCatequista
from custom_user.models import CustomUser
from django.core.exceptions import ValidationError

class SolicitudCatequistaForm(forms.ModelForm):
    class Meta:
        model = SolicitudCatequista
        fields = ['nombre','apellidos','email','disponibilidad','preferencias']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Ya existe una cuenta con este email.")
        return email
