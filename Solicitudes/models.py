from django.db import models
from Usuarios.models import Cliente, Proveedor
from Servicios.models import Servicio

class Solicitud_Presupuesto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    tipo_evento = models.CharField(max_length=100)
    fecha = models.DateField()
    duracion = models.FloatField()
    personas = models.IntegerField()
    direccion = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')])
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)