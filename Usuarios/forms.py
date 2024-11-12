from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
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
    foto_identificacion = forms.ImageField(required=True, label='Foto de Identificación')
    foto_rostro = forms.ImageField(required=True, label='Foto del Rostro')

    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_completo', 'email', 'password1', 'password2', 'foto_identificacion', 'foto_rostro']  # Campos presentes en el formulario

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
    foto_identificacion = forms.ImageField(required=True, label='Foto de Identificación')
    foto_rostro = forms.ImageField(required=True, label='Foto del Rostro')

    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_empresa', 'email', 'password1', 'password2', 'foto_identificacion', 'foto_rostro']

    # Funcion para guardar el usuario
    def save(self, commit=True):
        user = super().save(commit=False)
        user.es_proveedor = True  # Marcamos al usuario como proveedor
        if commit:
            user.save() #Guarda al usuario en la tabla User
        return user
    
class InicioSesionForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        label=''  # Esto elimina el label automático
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    
    #Funcion que valida los datos de inicio de sesion
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("Correo o contraseña incorrecta")
        return self.cleaned_data
    