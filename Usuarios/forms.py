from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

#Formulario para el registro de clientes
class RegistroClienteForm(UserCreationForm):
    nombre_completo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
        label=''  # Esto elimina el label automático
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        label=''  # Esto elimina el label automático
    )
    password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirma tu contraseña'})
    )

    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_completo', 'email', 'password1',
                  'password2']  # Campos presentes en el formulario

    # Funcion para guardar el usuario
    def save(self, commit=True):
        user = super().save(commit=False)
        user.es_cliente = True  # Marcamos al usuario como cliente
        if commit:
            user.save()
        return user
