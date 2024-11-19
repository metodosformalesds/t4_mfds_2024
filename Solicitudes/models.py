from django.db import models
from Usuarios.models import Cliente, Proveedor
from Servicios.models import Servicio

class Solicitud_Presupuesto(models.Model):
    """
    Modelo que representa una solicitud de presupuesto para un servicio.

    Descripción detallada:
    El modelo `Solicitud_Presupuesto` almacena la información relacionada con una solicitud
    de presupuesto realizada por un cliente para un servicio ofrecido por un proveedor. 
    Incluye detalles como el cliente, el proveedor, el servicio solicitado, el tipo de evento, 
    la fecha, la duración, el número de personas, la dirección, el estado de la solicitud, y el precio.

    Atributos:
        cliente (ForeignKey): Relación con el modelo `Cliente`, indica el cliente que realizó la solicitud.
        proveedor (ForeignKey): Relación con el modelo `Proveedor`, indica el proveedor que ofrece el servicio.
        servicio (ForeignKey): Relación con el modelo `Servicio`, especifica el servicio solicitado.
        tipo_evento (CharField): Tipo de evento para el cual se solicita el servicio (e.g., boda, cumpleaños).
        fecha (DateField): Fecha del evento.
        duracion (FloatField): Duración del evento en horas.
        personas (IntegerField): Número de personas que asistirán al evento.
        direccion (CharField): Dirección completa del evento.
        status (CharField): Estado de la solicitud, con opciones:
            - 'pendiente': La solicitud está en espera de respuesta del proveedor.
            - 'aceptada': La solicitud ha sido aceptada por el proveedor.
            - 'rechazada': La solicitud ha sido rechazada.
        precio (DecimalField): Precio propuesto para el servicio, puede ser `null` o estar vacío.
    """
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