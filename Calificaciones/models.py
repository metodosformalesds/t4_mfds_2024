from django.db import models
from Usuarios.models import Cliente  # Importa el modelo Cliente según corresponda

class Calificacion(models.Model):
    """
    Clase implementada por Alan
    Modelo que representa una calificacion de un servicio.

    Este modelo almacena las calificaciones y comentarios dejados por los usuarios para un servicio.
    Cada reseña incluye información sobre el servicio evaluado, el usuario que dejó la reseña, la
    calificación otorgada, un comentario opcional y la fecha en que se creó.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey('Servicios.Servicio', on_delete=models.CASCADE)  # Notación de cadena
    estrellas = models.IntegerField()  # De 0 a 5
    resenia = models.TextField()
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('cliente', 'servicio')
