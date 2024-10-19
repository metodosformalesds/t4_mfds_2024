from django.contrib import admin
from Solicitudes.models import Solicitud_Presupuesto

#Arega las tablas creadas al panel de Admin
admin.site.register(Solicitud_Presupuesto)
