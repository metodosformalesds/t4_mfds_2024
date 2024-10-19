from django.db import models
from Usuarios.models import User

class Notificacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_notificacion = models.CharField(max_length=100, choices=[('solicitud_presupuesto', 'Solicitud de Presupuesto'), ('confirmacion_pago', 'Confirmacion de Pago'), ('respuesta_solicitud', 'Respuesta de Solicitud'), ('calificar_servicio', 'Calificar Servicio')])
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True) #Se llena al momento de crear un registro
    leido = models.BooleanField(default=False)