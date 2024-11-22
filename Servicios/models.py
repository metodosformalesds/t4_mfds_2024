from django.db import models
from Usuarios.models import Proveedor
from django.conf import settings


class Servicio(models.Model):
    """
    Clase implementada por Alan
    Modelo que representa un servicio ofrecido por un proveedor.

    Este modelo almacena la información relacionada con un servicio que un proveedor puede ofrecer
    a través de la plataforma. Incluye datos básicos como el nombre, la categoría, el precio mínimo,
    y detalles adicionales como la dirección y el promedio de calificación.

    Campos:
        proveedor (ForeignKey): Relación con el modelo `Proveedor`. Indica el proveedor que ofrece el servicio.
        nombre (CharField): Nombre del servicio (máximo 255 caracteres).
        categoria (CharField): Categoría a la que pertenece el servicio (máximo 255 caracteres).
        direccion (CharField): Dirección detallada donde se ofrece el servicio (máximo 500 caracteres).
        precio_minimo (DecimalField): Precio mínimo del servicio con dos decimales.
        informacion_detallada (TextField): Descripción detallada del servicio.
        promedio_calificacion (DecimalField): Calificación promedio del servicio. Valor máximo: 9.99 con dos decimales.
            Por defecto es 0.0 si no tiene calificaciones.

    Métodos:
        __str__():
            Devuelve una representación en cadena del servicio, incluyendo su nombre y el proveedor
            que lo ofrece.
    """
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255)
    direccion = models.CharField(max_length=500)
    precio_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    informacion_detallada = models.TextField()
    promedio_calificacion = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    def __str__(self):
        return self.nombre + ' - por ' + self.proveedor.nombre_empresa
    
class Imagenes_Servicios(models.Model):
    """
    Clase implementada por Alan
    Modelo que representa las imágenes asociadas a un servicio.

    Este modelo almacena las imágenes relacionadas con un servicio en la plataforma. Cada imagen
    está vinculada a un servicio específico y se guarda en una carpeta específica dentro del sistema
    de archivos del proyecto.

    Campos:
        servicio (ForeignKey): Relación con el modelo `Servicio`. Indica a qué servicio pertenece la imagen.
        imagen (ImageField): Archivo de imagen cargado, que se guarda en la ruta `media/servicios/`.
    """
    servicio = models.ForeignKey(Servicio, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='servicios/') #Las imagenes se guardan en la carpeta /media/servicios/ en de la raiz del proyecto


class Reseña(models.Model):
    """
    Modelo que representa una reseña de un servicio.

    Este modelo almacena las calificaciones y comentarios dejados por los usuarios para un servicio.
    Cada reseña incluye información sobre el servicio evaluado, el usuario que dejó la reseña, la
    calificación otorgada, un comentario opcional y la fecha en que se creó.

    Campos:
        servicio (ForeignKey): Relación con el modelo `Servicio`. Indica el servicio que fue evaluado.
        usuario (ForeignKey): Relación con el modelo de usuario (`AUTH_USER_MODEL`). Indica quién dejó la reseña.
        calificacion (PositiveSmallIntegerField): Calificación otorgada al servicio (valor entero positivo).
        comentario (TextField): Comentario opcional sobre el servicio. Puede ser nulo o estar en blanco.
        fecha (DateTimeField): Fecha y hora en que se creó la reseña. Se establece automáticamente.
    """
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="reseñas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)