from django.urls import path
from . import views

urlpatterns = [
    path('solicitar_presupuesto/<int:servicio_id>/', views.solicitar_presupuesto, name='solicitar_presupuesto'),
]