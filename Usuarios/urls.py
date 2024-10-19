from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='index'),
    path('acerca_de/', views.acerca_de, name='acerca_de'),
    path('registro_cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro_proveedor/', views.registro_proveedor, name='registro_proveedor'),
    path('inicio_sesion/', views.inicio_sesion, name='inicio_sesion'),
    path('publicar_servicio/', views.publicar_servicio, name='publicar_servicio'),
]