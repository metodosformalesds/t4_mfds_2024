from django.db import models
from Usuarios.models import Proveedor
from django.conf import settings


class Servicio(models.Model):
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
    servicio = models.ForeignKey(Servicio, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='servicios/') #Las imagenes se guardan en la carpeta /media/servicios/ en de la raiz del proyecto


class Reseña(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="reseñas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)