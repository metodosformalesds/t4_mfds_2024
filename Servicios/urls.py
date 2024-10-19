from django.urls import path
from . import views

urlpatterns = [
    path('', views.servicios_sin_login, name='servicios_sin_login'),
]
