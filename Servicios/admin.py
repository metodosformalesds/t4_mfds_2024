from django.contrib import admin
from Servicios.models import Servicio, Imagenes_Servicios

#Arega las tablas creadas al panel de Admin
admin.site.register(Servicio)
admin.site.register(Imagenes_Servicios)
