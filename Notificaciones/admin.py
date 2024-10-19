from django.contrib import admin
from Notificaciones.models import Notificacion

#Arega las tablas creadas al panel de Admin
admin.site.register(Notificacion)
