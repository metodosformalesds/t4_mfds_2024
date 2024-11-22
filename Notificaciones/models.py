from django.db import models
from Usuarios.models import User
from Solicitudes.models import Solicitud_Presupuesto

class Notificacion(models.Model):
    """
    Clase implementada por Alan
    Modelo que representa una notificación dentro del sistema.

    Este modelo almacena notificaciones enviadas a los usuarios, relacionadas con diferentes
    eventos, como solicitudes de presupuesto, confirmaciones de pago, respuestas a solicitudes,
    y recordatorios para calificar servicios.

    Campos:
        user (ForeignKey): Relación con el modelo `User`. Indica el usuario al que se dirige la notificación.
        solicitud (ForeignKey, opcional): Relación con el modelo `Solicitud_Presupuesto`. 
            Asociada a la solicitud que genera la notificación (puede ser nula o estar vacía).
        tipo_notificacion (CharField): Tipo de la notificación. Opciones disponibles:
            - `Solicitud de Presupuesto`: Notifica la creación de una nueva solicitud.
            - `Confirmacion de Pago`: Informa sobre un pago confirmado.
            - `Respuesta de Solicitud`: Indica que la solicitud ha recibido una respuesta.
            - `Calificar Servicio`: Solicita al usuario calificar un servicio.
        fecha (DateTimeField): Fecha y hora en que se creó la notificación. Se genera automáticamente al crear el registro.
        leido (BooleanField): Indica si la notificación ha sido marcada como leída por el usuario. Por defecto es `False`.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solicitud = models.ForeignKey(Solicitud_Presupuesto, on_delete=models.CASCADE, null=True, blank=True)
    tipo_notificacion = models.CharField(max_length=100, choices=[
        ('Solicitud de Presupuesto', 'Solicitud de Presupuesto'), 
        ('Confirmacion de Pago', 'Confirmacion de Pago'), 
        ('Respuesta de Solicitud', 'Respuesta de Solicitud'), 
        ('Calificar Servicio', 'Calificar Servicio')])
    fecha = models.DateTimeField(auto_now_add=True) #Se llena al momento de crear un registro
    leido = models.BooleanField(default=False)