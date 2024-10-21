from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
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
        fields = ['nombre_completo', 'email', 'password1', 'password2']  # Campos presentes en el formulario

    # Funcion para guardar el usuario
    def save(self, commit=True):
        user = super().save(commit=False)
        user.es_cliente = True  # Marcamos al usuario como cliente
        if commit:
            user.save() #Guarda al usuario en la tabla User
        return user

class RegistroProveedorForm(UserCreationForm):
    nombre_empresa = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de la empresa'}),
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
    clabe = forms.CharField(
        max_length=18,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'CLABE'}),
        label='Ingresa la CLABE interbancaria de la cuenta donde deseas recibir los pagos'
    )

    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_empresa', 'email', 'password1', 'password2', 'clabe']  # Campos presentes en el formulario
    
    #Funcion para validar que la clabe sean 18 caracteres
    def clean_clabe(self):
        clabe = self.cleaned_data.get('clabe')
        if len(clabe) != 18:
            raise ValidationError('La CLABE debe tener exactamente 18 caracteres.')
        return clabe

    # Funcion para guardar el usuario
    def save(self, commit=True):
        user = super().save(commit=False)
        user.es_proveedor = True  # Marcamos al usuario como proveedor
        if commit:
            user.save() #Guarda al usuario en la tabla User
        return user