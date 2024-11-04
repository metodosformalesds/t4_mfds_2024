from django.db import models
from Usuarios.models import User
from Solicitudes.models import Solicitud_Presupuesto

class Notificacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solicitud = models.ForeignKey(Solicitud_Presupuesto, on_delete=models.CASCADE, null=True, blank=True)
    tipo_notificacion = models.CharField(max_length=100, choices=[
        ('Solicitud de Presupuesto', 'Solicitud de Presupuesto'), 
        ('Confirmacion de Pago', 'Confirmacion de Pago'), 
        ('Respuesta de Solicitud', 'Respuesta de Solicitud'), 
        ('Calificar Servicio', 'Calificar Servicio')])
    fecha = models.DateTimeField(auto_now_add=True) #Se llena al momento de crear un registro
    leido = models.BooleanField(default=False)