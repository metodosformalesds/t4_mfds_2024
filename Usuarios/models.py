from django.db import models
from django.contrib.auth.models import AbstractUser

#Extension del modelo de usuarios de django para clientes y proveedores
class User(AbstractUser):
    email = models.EmailField(unique=True, default='default@example.com')
    es_cliente = models.BooleanField(default=False)
    es_proveedor = models.BooleanField(default=False)
    registro_con_google = models.BooleanField(default=False)
    registro_con_facebook = models.BooleanField(default=False)
    registro_con_ios = models.BooleanField(default=False)
    
    username = None  # Desactiva el campo de username
    
    USERNAME_FIELD = 'email' # Se cambia el USERNAME_FIELD para usar el email
    REQUIRED_FIELDS = []  # Se deja vacío para que solo se requiera el email y la contraseña
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=255, blank=False, default='')
    
#Modelo para proveedores derivado de User
class Proveedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=255)
    clabe = models.CharField(max_length=18)
