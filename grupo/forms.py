from django import forms
from custom_user.models import CustomUser
from .models import Grupo

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
