from django.urls import path
from . import views

urlpatterns = [
    path('', views.servicios_sin_login, name='servicios_sin_login'),
    path('publicar_servicio/', views.publicar_servicio, name='publicar_servicio'),
    path('publicacion_servicio/<int:id>/', views.publicacion_servicio, name='publicacion_servicio'), 
     path('servicios/', views.service_list, name='service_list'),
]
