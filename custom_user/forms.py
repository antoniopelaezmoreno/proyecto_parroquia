from django import forms
from .models import CustomUser
from django.core.validators import RegexValidator

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar_password = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)
    telefono = forms.CharField(label='Teléfono', max_length=9,validators=[RegexValidator(r'^\d{9}$', message="El número de teléfono debe tener exactamente 9 dígitos.")])

    class Meta:
        model = CustomUser
        fields = ['password', 'confirmar_password', 'telefono']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.telefono = self.cleaned_data['telefono']
        if commit:
            user.save()
        return user
    
class EditCustomUserForm(forms.ModelForm):
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'email': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #c3c3c3;'})
        }

    def save(self, commit=True):
        user = super(EditCustomUserForm, self).save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
    
