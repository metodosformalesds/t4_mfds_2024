from django.urls import path
from . import views

urlpatterns = [
    path('solicitar_presupuesto/<int:servicio_id>/', views.solicitar_presupuesto, name='solicitar_presupuesto'),
    path('obtener_solicitud/<int:solicitud_id>/', views.obtener_solicitud, name='obtener_solicitud'),
    path('responder_solicitud/<int:solicitud_id>/', views.responder_solicitud, name='responder_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('rechazar_respuesta/<int:solicitud_id>/', views.rechazar_respuesta, name='rechazar_respuesta'),
]