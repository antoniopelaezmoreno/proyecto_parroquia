from django import forms
from .models import Sesion
from drive.models import Archivo

class SesionForm(forms.ModelForm):
    archivos = forms.ModelMultipleChoiceField(queryset=Archivo.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivos'].label_from_instance = lambda obj: obj.name
        # Establecer el valor predeterminado de la fecha si está disponible
        if self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%d')

    class Meta:
        model = Sesion
        fields = ['titulo', 'descripcion', 'fecha', 'archivos']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }

