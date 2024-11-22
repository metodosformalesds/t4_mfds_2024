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
    """
    Funcion implementada por Alan
    Solicita un presupuesto para un servicio específico.

    Esta función permite a un usuario autenticado enviar una solicitud de presupuesto para un 
    servicio ofrecido por un proveedor. La función valida los datos proporcionados por el 
    usuario, crea un registro en la base de datos y notifica al proveedor sobre la solicitud.
    
    Proceso:
        1. Obtiene el servicio especificado por `servicio_id`.
        2. Valida los datos del formulario enviado mediante POST.
        3. Si los datos son válidos:
            - Crea un registro en la base de datos para la solicitud de presupuesto.
            - Asigna el cliente, proveedor, servicio y estado inicial a la solicitud.
            - Construye y guarda la dirección completa a partir de los datos del formulario.
            - Crea una notificación para el proveedor informándole de la nueva solicitud.
        4. Si los datos del formulario no son válidos, retorna los errores en formato JSON.

    Decoradores:
        @csrf_exempt: Desactiva la protección CSRF para esta vista.
        @login_required: Requiere que el usuario esté autenticado para acceder a esta función.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.
        servicio_id (int): El ID del servicio para el cual se solicita el presupuesto.

    Returns:
        JsonResponse: Una respuesta JSON con el estado de la operación:
            - `status: success`: Si la solicitud fue creada exitosamente.
            - `status: error`: Si hubo errores en la validación del formulario o si el método no es POST.
    """
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
    """
    Funcion implementada por Alan
    Obtiene los detalles de una solicitud de presupuesto específica.
    
    Esta función devuelve un objeto JSON con los detalles de la solicitud de presupuesto
    especificada por `solicitud_id`. La función utiliza el modelo `Solicitud_Presupuesto`
    para obtener la solicitud y construye un objeto JSON con los campos solicitados.
    
    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.
        solicitud_id (int): El ID de la solicitud de presupuesto a obtener.
    
    Returns:
        JsonResponse: Un objeto JSON con los detalles de la solicitud de presupuesto.
    """
    solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)
    data = {
        'servicio': solicitud.servicio.nombre,
        'proveedor': solicitud.proveedor.nombre_empresa,
        'proveedor_contacto': solicitud.proveedor.user.email,
        'cliente': solicitud.cliente.nombre_completo,
        'cliente_contacto': solicitud.cliente.user.email,
        'personas': solicitud.personas,
        'duracion': solicitud.duracion,
        'status': solicitud.status,
        'fecha': solicitud.fecha.strftime('%Y-%m-%d'),
        'tipo_evento': solicitud.tipo_evento,
        'direccion': solicitud.direccion,
        'precio': solicitud.precio
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def responder_solicitud(request, solicitud_id):
    """
    Funcion implementada por Alan
    Responde a una solicitud de presupuesto.

    Esta función permite al proveedor responder a una solicitud de presupuesto creada por un cliente. 
    El proveedor puede actualizar el precio de la solicitud y cambiar su estado a 'aceptada'. Además, 
    se generan notificaciones tanto para el cliente como para el proveedor.

    Proceso:
        1. Verifica que el método de la solicitud sea POST.
        2. Recupera la solicitud de presupuesto especificada por `solicitud_id`.
        3. Verifica que el proveedor que responde sea el dueño del servicio relacionado con la solicitud.
        4. Obtiene el precio de la solicitud del cuerpo de la petición (`request.body`).
        5. Si el precio está presente:
            - Actualiza el precio de la solicitud.
            - Cambia el estado de la solicitud a 'aceptada'.
            - Guarda los cambios en la base de datos.
            - Crea una notificación para el cliente informándole de la respuesta.
            - Marca como leída la notificación original que el proveedor recibió.
        6. Si el precio no está presente, retorna un error con un mensaje explicativo.
        7. Si el método no es POST, retorna un error indicando que el método no está permitido.
        
    Decoradores:
        @csrf_exempt: Desactiva la protección CSRF para esta vista.
        @login_required: Requiere que el usuario esté autenticado para acceder a esta función.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.
        solicitud_id (int): El ID de la solicitud de presupuesto que el proveedor quiere responder.
        
    Returns:
        JsonResponse: Una respuesta JSON con el estado de la operación:
            - `status: success`: Si la solicitud fue respondida exitosamente.
            - `status: error`: Si hubo un error durante la operación (por ejemplo, falta de permisos, datos incompletos o método no permitido).
    """
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
    """
    Funcion implementada por Alan
    Rechaza una solicitud de presupuesto.

    Esta función permite al proveedor rechazar una solicitud de presupuesto creada por un cliente. 
    Actualiza el estado de la solicitud a 'rechazada' y marca como leída la notificación asociada 
    que el proveedor recibió originalmente.
    
    Proceso:
        1. Recupera la solicitud de presupuesto especificada por `solicitud_id`.
        2. Verifica que el usuario actual sea el proveedor asociado a la solicitud.
        3. Si el método de la solicitud es POST:
            - Actualiza el estado de la solicitud a 'rechazada'.
            - Guarda los cambios en la base de datos.
            - Marca como leída la notificación asociada al proveedor.
        4. Si el método no es POST, retorna un error indicando que el método no está permitido.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado para acceder a esta función.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.
        solicitud_id (int): El ID de la solicitud de presupuesto que se desea rechazar.

    Returns:
        JsonResponse: Una respuesta JSON con el estado de la operación:
            - `status: success`: Si la solicitud fue rechazada exitosamente.
            - `status: error`: Si hubo un error durante la operación (por ejemplo, falta de permisos o método no permitido).
    """
    solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)

    # Verifica que el usuario actual sea el proveedor de la solicitud
    if solicitud.proveedor.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para rechazar esta solicitud'}, status=403)

    if request.method == 'POST':
        # Actualiza el estado de la solicitud a 'rechazada'
        solicitud.status = 'rechazada'
        solicitud.save()

        # Marcar la notificación original como leída
        notificacion_proveedor = Notificacion.objects.filter(user=request.user, solicitud=solicitud, tipo_notificacion='Solicitud de Presupuesto', leido=False).first()
        if notificacion_proveedor:
            notificacion_proveedor.leido = True
            notificacion_proveedor.save()

        return JsonResponse({'status': 'success', 'message': 'Solicitud rechazada exitosamente'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
@login_required
def rechazar_respuesta(request, solicitud_id):
    """
    Funcion implementada por Alan
    Rechaza la respuesta de una solicitud de presupuesto.

    Esta función permite al cliente rechazar la respuesta de una solicitud de presupuesto enviada 
    por el proveedor. Cambia el estado de la solicitud a 'rechazada' y marca como leída la 
    notificación original asociada al cliente.
    
    Proceso:
        1. Recupera la solicitud de presupuesto especificada por `solicitud_id`.
        2. Verifica que el usuario actual sea el cliente asociado a la solicitud.
        3. Si el método de la solicitud es POST:
            - Actualiza el estado de la solicitud a 'rechazada'.
            - Guarda los cambios en la base de datos.
            - Marca como leída la notificación asociada al cliente.
        4. Si el método no es POST, retorna un error indicando que el método no está permitido.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado para acceder a esta función.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.
        solicitud_id (int): El ID de la solicitud de presupuesto que se desea rechazar.

    Returns:
        JsonResponse: Una respuesta JSON con el estado de la operación:
            - `status: success`: Si la solicitud fue rechazada exitosamente.
            - `status: error`: Si hubo un error durante la operación (por ejemplo, falta de permisos o método no permitido).
    """
    solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)

    # Verifica que el usuario actual sea el cliente de la solicitud
    if solicitud.cliente.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para rechazar esta solicitud'}, status=403)

    if request.method == 'POST':
        # Actualiza el estado de la solicitud a 'rechazada'
        solicitud.status = 'rechazada'
        solicitud.save()

        # Marcar la notificación original como leída
        notificacion_cliente = Notificacion.objects.filter(user=request.user, solicitud=solicitud, tipo_notificacion='Respuesta de Solicitud', leido=False).first()
        if notificacion_cliente:
            notificacion_cliente.leido = True
            notificacion_cliente.save()

        return JsonResponse({'status': 'success', 'message': 'Solicitud rechazada exitosamente'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)