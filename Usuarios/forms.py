from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User

#Formulario para el registro de clientes
class RegistroClienteForm(UserCreationForm):
    """
    Clase implementada por Alan
    Formulario para el registro de clientes.

    Este formulario hereda de `UserCreationForm` y permite a los usuarios registrarse como clientes en el sistema.
    Además de los campos estándar de usuario y contraseña, incluye campos personalizados como nombre completo,
    correo electrónico, y fotos de identificación y rostro.

    Campos:
        nombre_completo (CharField): Campo obligatorio para ingresar el nombre completo del cliente.
        email (EmailField): Campo obligatorio para ingresar el correo electrónico del cliente.
        password1 (CharField): Campo para ingresar la contraseña (heredado de `UserCreationForm`).
        password2 (CharField): Campo para confirmar la contraseña (heredado de `UserCreationForm`).
        foto_identificacion (ImageField): Campo obligatorio para subir una foto de identificación.
        foto_rostro (CharField): Campo oculto para capturar una foto del rostro desde la cámara.

    Meta:
        model (User): Modelo relacionado para la creación del usuario.
        fields (list): Campos que aparecerán en el formulario, incluyendo los personalizados.

    Métodos:
        save(commit=True):
            Sobrescribe el método `save` para marcar al usuario como cliente (`es_cliente = True`) antes de guardarlo.
            - Si `commit` es `True`, guarda el usuario en la base de datos.
            - Devuelve la instancia del usuario.
    """
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
    foto_identificacion = forms.ImageField(
        required=True, 
        label='Foto de Identificación'
    )
    foto_rostro = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Foto del Rostro (capturada desde la cámara)'
    )

    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_completo', 'email', 'password1', 'password2', 'foto_identificacion', 'foto_rostro']  # Campos presentes en el formulario

    # Funcion para guardar el usuario
    def save(self, commit=True):
        """
        Funcion implementada por Alan
        Guarda el usuario registrado.

        Sobrescribe el método `save` del formulario para realizar personalizaciones antes de guardar el usuario.
        Marca al usuario como cliente (`es_cliente = True`) antes de guardarlo.

        Args:
            commit (bool): Indica si el usuario debe guardarse inmediatamente en la base de datos.

        Returns:
            User: La instancia del usuario creada o modificada.
        """
        user = super().save(commit=False)
        user.es_cliente = True  # Marcamos al usuario como cliente
        if commit:
            user.save() #Guarda al usuario en la tabla User
        return user

class RegistroProveedorForm(UserCreationForm):
    """
    Clase implementada por Alan
    Formulario para el registro de proveedores.

    Este formulario hereda de `UserCreationForm` y permite a los usuarios registrarse como proveedores en el sistema.
    Además de los campos estándar de usuario y contraseña, incluye campos personalizados como nombre de la empresa,
    correo electrónico, y fotos de identificación y rostro.

    Campos:
        nombre_empresa (CharField): Campo obligatorio para ingresar el nombre de la empresa del proveedor.
        email (EmailField): Campo obligatorio para ingresar el correo electrónico del proveedor.
        password1 (CharField): Campo para ingresar la contraseña (heredado de `UserCreationForm`).
        password2 (CharField): Campo para confirmar la contraseña (heredado de `UserCreationForm`).
        foto_identificacion (ImageField): Campo obligatorio para subir una foto de identificación.
        foto_rostro (CharField): Campo oculto para capturar una foto del rostro desde la cámara (opcional).

    Meta:
        model (User): Modelo relacionado para la creación del usuario.
        fields (list): Campos que aparecerán en el formulario, incluyendo los personalizados.

    Métodos:
        save(commit=True):
            Sobrescribe el método `save` para marcar al usuario como proveedor (`es_proveedor = True`) antes de guardarlo.
            - Si `commit` es `True`, guarda el usuario en la base de datos.
            - Devuelve la instancia del usuario.
    """
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
    foto_identificacion = forms.ImageField(
        required=True, 
        label='Foto de Identificación'
    )
    foto_rostro = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Foto del Rostro (capturada desde la cámara)'
    )
    class Meta:
        model = User  # Se define el modelo a utilizar
        fields = ['nombre_empresa', 'email', 'password1', 'password2', 'foto_identificacion', 'foto_rostro']

    # Funcion para guardar el usuario
    def save(self, commit=True):
        """
        Funcion implementada por Alan
        Guarda el usuario registrado.

        Sobrescribe el método `save` del formulario para realizar personalizaciones antes de guardar el usuario.
        Marca al usuario como proveedor (`es_proveedor = True`) antes de guardarlo.

        Args:
            commit (bool): Indica si el usuario debe guardarse inmediatamente en la base de datos.

        Returns:
            User: La instancia del usuario creada o modificada.
        """
        user = super().save(commit=False)
        user.es_proveedor = True  # Marcamos al usuario como proveedor
        if commit:
            user.save() #Guarda al usuario en la tabla User
        return user
    
class InicioSesionForm(forms.Form):
    """
    Clase implementada por Alan
    Formulario de inicio de sesión.

    Este formulario permite a los usuarios ingresar sus credenciales (correo electrónico y contraseña)
    para autenticarse en el sistema.

    Campos:
        email (EmailField): Campo obligatorio para ingresar el correo electrónico del usuario.
        password (CharField): Campo obligatorio para ingresar la contraseña del usuario.

    Métodos:
        clean():
            Realiza la validación de los datos ingresados. Comprueba si las credenciales coinciden
            con un usuario existente en el sistema. Si no son válidas, lanza un error de validación.
    """
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
        """
        Funcion implementada por Alan
        Valida los datos de inicio de sesión.

        Este método valida que las credenciales ingresadas (correo y contraseña) coincidan con un usuario
        existente en el sistema. Utiliza el método `authenticate` para verificar las credenciales.

        Raises:
            ValidationError: Si el correo o la contraseña son incorrectos.

        Returns:
            dict: Los datos limpiados (`cleaned_data`) si las credenciales son válidas.
        """
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("Correo o contraseña incorrecta")
        return self.cleaned_data
    