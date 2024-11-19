from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='index'),
    path('acerca_de/', views.acerca_de, name='acerca_de'),
    path('registro_cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro_proveedor/', views.registro_proveedor, name='registro_proveedor'),
    path('inicio_sesion/', views.inicio_sesion, name='inicio_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('accounts/', include('allauth.urls')),#Google
    path('captura_bio/', views.captura_bio, name='captura_bio'),
    path('get_temp_image/', views.get_temp_image, name='get_temp_image'),

]
