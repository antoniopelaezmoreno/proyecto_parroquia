from django import forms
from custom_user.models import CustomUser
from .models import Grupo
from catecumeno.models import Catecumeno

class GrupoForm(forms.ModelForm):
    def __init__(self, *args, catequistas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if catequistas:
            self.fields['catequista1'].queryset = catequistas
            self.fields['catequista2'].queryset = catequistas
        else:
            self.fields['catequista1'].queryset = CustomUser.objects.none()
            self.fields['catequista2'].queryset = CustomUser.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        catequista1 = cleaned_data.get('catequista1')
        catequista2 = cleaned_data.get('catequista2')

        if catequista1 == catequista2:
            raise forms.ValidationError("Los catequistas deben ser diferentes.")
        
        return cleaned_data

    class Meta:
        model = Grupo
        fields = ['catequista1', 'catequista2']

class GrupoAdminForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['catequista1', 'catequista2', 'ciclo']

    def __init__(self, *args, **kwargs):
        super(GrupoAdminForm, self).__init__(*args, **kwargs)
        self.fields['catequista1'].queryset = CustomUser.objects.none()
        self.fields['catequista2'].queryset = CustomUser.objects.none()

        if 'ciclo' in self.data:
            try:
                ciclo_id = int(self.data.get('ciclo'))
                # Filtrar los catequistas basados en el ciclo seleccionado
                self.fields['catequista1'].queryset = CustomUser.objects.filter(ciclo=ciclo_id)
                self.fields['catequista2'].queryset = CustomUser.objects.filter(ciclo=ciclo_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Si es una instancia existente, filtrar los catequistas basados en el ciclo de la instancia
            ciclo_id = self.instance.ciclo
            self.fields['catequista1'].queryset = CustomUser.objects.filter(ciclo=ciclo_id)
            self.fields['catequista2'].queryset = CustomUser.objects.filter(ciclo=ciclo_id)
