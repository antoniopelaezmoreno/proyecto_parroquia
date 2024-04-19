from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['password']

    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
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
    
