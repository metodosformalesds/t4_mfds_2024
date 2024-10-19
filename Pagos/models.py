from django.db import models
from Usuarios.models import Cliente
from Servicios.models import Servicio

class Contratacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado_transaccion = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('completada', 'Completada')])
    fecha_contratacion = models.DateField()
