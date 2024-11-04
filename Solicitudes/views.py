from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SolicitudPresupuestoClienteForm
from Servicios.models import Servicio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Notificaciones.models import Notificacion
from .models import Solicitud_Presupuesto
import json

@csrf_exempt
@login_required #Decorado para asegurarse de que el usuario haya iniciado sesión
def solicitar_presupuesto(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)  # Verifica que el servicio exista y lo obtiene
    proveedor = servicio.proveedor

    if request.method == 'POST':
        form = SolicitudPresupuestoClienteForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.cliente = request.user.cliente  # Asigna el id del cliente
            solicitud.proveedor = proveedor # Asigna el id del proveedor
            solicitud.servicio = servicio # Asigna el id del servicio
            solicitud.status = 'pendiente'  # Estado inicial
            # Concatena los datos que conforman la dirección
            solicitud.direccion = f"{form.cleaned_data['calle']}, {form.cleaned_data['numero_exterior']} {form.cleaned_data.get('numero_interior', '')}, {form.cleaned_data['colonia']}, {form.cleaned_data['codigo_postal']}"
            solicitud.save()  # Guarda la solicitud en la base de datos
            
            #Crea una notificacion para el proveedor
            Notificacion.objects.create(
                user=proveedor.user, 
                solicitud=solicitud,
                tipo_notificacion='Solicitud de Presupuesto',
                leido=False #Por defecto no leido
            )
            
            return JsonResponse({'status': 'success', 'message': 'Solicitud enviada exitosamente'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    
def obtener_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)
    data = {
        'servicio': solicitud.servicio.nombre,
        'cliente': solicitud.cliente.nombre_completo,
        'personas': solicitud.personas,
        'duracion': solicitud.duracion,
        'status': solicitud.status,
        'fecha': solicitud.fecha.strftime('%Y-%m-%d'),
        'tipo_evento': solicitud.tipo_evento,
        'direccion': solicitud.direccion
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def responder_solicitud(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)

        # Solo el proveedor relacionado con la solicitud puede responderla
        if solicitud.proveedor.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'No tienes permiso para responder esta solicitud'}, status=403)

        data = json.loads(request.body)
        precio = data.get('precio')

        if precio is not None:
            # Actualiza el precio de la solicitud
            solicitud.precio = precio
            solicitud.status = 'aceptada'  # Cambia el estado a 'aceptada'
            solicitud.save()

            # Crea una notificación para el cliente
            Notificacion.objects.create(
                user=solicitud.cliente.user,  # Cliente que hizo la solicitud
                solicitud=solicitud,
                tipo_notificacion='Respuesta de Solicitud',
                leido=False
            )
            
            # Marcar como leída la notificación original que el proveedor recibió
            notificacion_proveedor = Notificacion.objects.filter(user=request.user, solicitud=solicitud, tipo_notificacion='Solicitud de Presupuesto').first()
            if notificacion_proveedor:
                notificacion_proveedor.leido = True
                notificacion_proveedor.save()

            return JsonResponse({'status': 'success', 'message': 'Solicitud respondida exitosamente'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Precio no especificado'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)

    # Verifica que el usuario actual sea el proveedor de la solicitud
    if solicitud.proveedor.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para rechazar esta solicitud'}, status=403)

    if request.method == 'POST':
        # Actualiza el estado de la solicitud a 'rechazada'
        solicitud.status = 'rechazada'
        solicitud.save()

        # Marcar la notificación original como leída
        notificacion_proveedor = Notificacion.objects.filter(user=request.user, solicitud=solicitud, tipo_notificacion='Solicitud de Presupuesto').first()
        if notificacion_proveedor:
            notificacion_proveedor.leido = True
            notificacion_proveedor.save()

        return JsonResponse({'status': 'success', 'message': 'Solicitud rechazada exitosamente'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)