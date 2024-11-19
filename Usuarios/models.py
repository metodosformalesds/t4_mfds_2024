from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

#Extension del modelo de usuarios de django para clientes y proveedores
class User(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema.

    Este modelo reemplaza el campo 'username' predeterminado de Django
    con el campo 'email' como identificador principal. También incluye
    campos adicionales para distinguir entre clientes y proveedores, y
    para rastrear los métodos de registro utilizados (Google, Facebook, iOS).

    Campos:
        email (EmailField): Correo electrónico único que actúa como identificador.
        es_cliente (BooleanField): Indica si el usuario es un cliente.
        es_proveedor (BooleanField): Indica si el usuario es un proveedor.
        registro_con_google (BooleanField): Indica si el usuario se registró con Google.
        registro_con_facebook (BooleanField): Indica si el usuario se registró con Facebook.
        registro_con_ios (BooleanField): Indica si el usuario se registró con iOS.
        groups (ManyToManyField): Grupos a los que pertenece el usuario (relación con el modelo 'auth.Group').
        user_permissions (ManyToManyField): Permisos específicos del usuario (relación con el modelo 'auth.Permission').

    Configuración:
        USERNAME_FIELD: Se establece como 'email' para usarlo como identificador principal.
        REQUIRED_FIELDS: Se deja vacío para requerir solo el correo y la contraseña.

    Manager:
        objects: Se utiliza un `UserManager` personalizado para manejar la creación y autenticación de usuarios.
    """
    email = models.EmailField(unique=True, default='default@example.com')
    es_cliente = models.BooleanField(default=False)
    es_proveedor = models.BooleanField(default=False)
    registro_con_google = models.BooleanField(default=False)
    registro_con_facebook = models.BooleanField(default=False)
    registro_con_ios = models.BooleanField(default=False)
    
    username = None  # Desactiva el campo de username
    
    USERNAME_FIELD = 'email' # Se cambia el USERNAME_FIELD para usar el email
    REQUIRED_FIELDS = []  # Se deja vacío para que solo se requiera el email y la contraseña
    objects = UserManager()  # Asocia el UserManager personalizado
    
    # Se cambia el related_name para evitar un conflicto entre dos nombres iguales
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='Usuarios_user_set',  # Este nombre es unico y evita el conflicto
        blank=True,
        help_text='Grupos a los que pertenece este usuario.',
        verbose_name='grupos'
    )
    
    # Se cambia el related_name para evitar un conflicto entre dos nombres iguales
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_user_set',  # Este nombre es unico y evita el conflicto
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='permisos'
    )

#Modelo para clientes derivado de User
class Cliente(models.Model):
    """
    Modelo que representa un cliente en el sistema.

    Este modelo está vinculado de forma directa al modelo de usuario personalizado (`User`)
    a través de una relación uno a uno. Se utiliza para almacenar información adicional
    específica de los clientes.

    Campos:
        user (OneToOneField): Relación uno a uno con el modelo `User`.
        nombre_completo (CharField): Nombre completo del cliente.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=255, blank=False, default='')
    
#Modelo para proveedores derivado de User
class Proveedor(models.Model):
    """
    Modelo que representa un proveedor en el sistema.

    Este modelo está vinculado de forma directa al modelo de usuario personalizado (`User`)
    a través de una relación uno a uno. Se utiliza para almacenar información adicional
    específica de los proveedores, como el nombre de la empresa y el ID de cuenta de Stripe
    para procesar pagos.

    Campos:
        user (OneToOneField): Relación uno a uno con el modelo `User`.
        nombre_empresa (CharField): Nombre de la empresa del proveedor.
        stripe_account_id (CharField): ID de la cuenta de Stripe del proveedor, utilizado para
            recibir pagos. Puede ser nulo o estar vacío.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=255)
    stripe_account_id = models.CharField(max_length=255, null=True, blank=True)
