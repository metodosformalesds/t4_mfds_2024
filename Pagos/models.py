from django.db import models
from Usuarios.models import Cliente
from Servicios.models import Servicio

class Contratacion(models.Model):
    """
    Clase implementada por Alan
    Modelo que representa una contratación de un servicio por parte de un cliente.

    Este modelo almacena la información relacionada con la contratación de un servicio,
    incluyendo detalles del cliente, el servicio contratado, el precio, el estado de la transacción,
    y un identificador único para la sesión de Stripe.

    Campos:
        cliente (ForeignKey): Relación con el modelo `Cliente`. Indica el cliente que contrata el servicio.
        servicio (ForeignKey): Relación con el modelo `Servicio`. Indica el servicio que fue contratado.
        precio (DecimalField): Precio total de la contratación, con dos decimales.
        estado_transaccion (CharField): Estado de la transacción, con las opciones:
            - `pendiente`: La transacción está en proceso.
            - `completada`: La transacción fue completada exitosamente.
        fecha_contratacion (DateField): Fecha en que se realizó la contratación.
        stripe_session_id (CharField): Identificador único de la sesión de Stripe asociado a la transacción.
            Puede ser nulo o estar vacío si no se utilizó Stripe.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado_transaccion = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('completada', 'Completada')])
    fecha_contratacion = models.DateField()
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Evita duplicados
