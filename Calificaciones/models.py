from django.db import models
from Usuarios.models import Cliente
from Servicios.models import Servicio

class Calificacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    estrellas = models.IntegerField()  # De 0 a 5
    resenia = models.TextField()
    fecha = models.DateField(auto_now_add=True) #Se llena al momento de crear un registro
