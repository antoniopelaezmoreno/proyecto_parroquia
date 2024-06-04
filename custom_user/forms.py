from django import forms
from .models import CustomUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar_password = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)
    telefono = forms.CharField(label='Teléfono', max_length=9,validators=[RegexValidator(r'^\d{9}$', message="El número de teléfono debe tener exactamente 9 dígitos.")])

    class Meta:
        model = CustomUser
        fields = ['password', 'confirmar_password', 'telefono']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password != confirmar_password:
            self.add_error('password', "Las contraseñas no coinciden")
        
    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.telefono = self.cleaned_data['telefono']
        if commit:
            user.save()
        return user
    
class EditCustomUserForm(forms.ModelForm):
    password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput, required=False)
    confirmar_password = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['nombre', 'apellidos', 'email', 'telefono']
        widgets = {
            'email': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #c3c3c3;'})
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password or confirmar_password:
            if password != confirmar_password:
                self.add_error('password', "Las contraseñas no coinciden")

    def save(self, commit=True):
        user = super(EditCustomUserForm, self).save(commit=False)
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
    
