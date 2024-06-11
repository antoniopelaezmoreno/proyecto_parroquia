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
        
        # Comprueba si los catequistas elegidos ya están en otro grupo del mismo ciclo
        if catequista1 and catequista2:
            if Grupo.objects.filter(ciclo=catequista1.ciclo, catequista1=catequista1).exclude(pk=self.instance.pk).exists() or Grupo.objects.filter(ciclo=catequista1.ciclo, catequista2=catequista1).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("El catequista 1 ya está en otro grupo del mismo ciclo.")
            if Grupo.objects.filter(ciclo=catequista2.ciclo, catequista2=catequista2).exclude(pk=self.instance.pk).exists() or Grupo.objects.filter(ciclo=catequista2.ciclo, catequista1=catequista2).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("El catequista 2 ya está en otro grupo del mismo ciclo.")
        
        return cleaned_data

    class Meta:
        model = Grupo
        fields = ['catequista1', 'catequista2']
