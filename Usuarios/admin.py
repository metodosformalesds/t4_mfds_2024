from django.contrib import admin
from Usuarios.models import User, Cliente, Proveedor

#Arega las tablas creadas al panel de Admin
admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Proveedor)