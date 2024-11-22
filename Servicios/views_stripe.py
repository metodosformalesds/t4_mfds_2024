import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect, render
from .models import Servicio
from Solicitudes.models import Solicitud_Presupuesto
from Notificaciones.models import Notificacion
from Pagos.models import Contratacion
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@csrf_exempt
def create_account(request):
    """
    Funcion implementada por Alan
    Crea una cuenta conectada de Stripe para un proveedor.

    Esta función permite a los proveedores crear una cuenta conectada de Stripe tipo "express",
    necesaria para recibir pagos a través de la plataforma. La cuenta se crea utilizando la API
    de Stripe y se almacena temporalmente en la sesión del usuario.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado.
        @csrf_exempt: Exime esta vista de la verificación CSRF, ya que interactúa con una API externa.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. 

    Funcionalidad:
        - Crea una cuenta conectada de Stripe con los siguientes parámetros:
            - `type`: Tipo de cuenta (express).
            - `country`: País del proveedor (actualmente configurado para "MX").
            - `email`: Correo electrónico del usuario autenticado.
            - `business_type`: Tipo de negocio ("individual").
            - `business_profile`: Perfil de negocio con descripción del producto.
        - Almacena el `stripe_account_id` en la sesión del usuario para su uso posterior.

    Returns:
        JsonResponse:
            - `account`: El ID de la cuenta conectada creada si la operación es exitosa.
            - `error`: Un mensaje de error y código de estado 500 si ocurre una excepción.
    """
    try:
        # Crea una cuenta conectada para el proveedor
        account = stripe.Account.create(
            type="express",
            country="MX",  # Cambia según el país de tu proveedor
            email=request.user.email,
            business_type="individual",
            business_profile={"product_description": "Proveedor de servicios en DecoRent"},
        )

        # Almacena el `stripe_account_id` temporalmente en la sesión
        request.session['stripe_account_id'] = account.id

        return JsonResponse({'account': account.id})
    except Exception as e:
        print(f"Error al crear la cuenta conectada: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
def create_account_link(request):
    """
    Funcion implementada por Alan
    Crea un enlace de cuenta conectada de Stripe para la configuración inicial.

    Esta función genera un enlace de configuración ("account_onboarding") para que un proveedor pueda
    completar el proceso de configuración de su cuenta conectada de Stripe. El enlace incluye URLs
    de retorno y actualización para manejar el flujo de configuración.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado.
        @csrf_exempt: Exime esta vista de la verificación CSRF, ya que interactúa con una API externa.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Debe contener un cuerpo JSON
                               con el ID de la cuenta conectada (`account`).

    Funcionalidad:
        - Decodifica el cuerpo de la solicitud para obtener los datos en formato JSON.
        - Recupera el `connected_account_id` proporcionado en el cuerpo de la solicitud.
        - Verifica que el `connected_account_id` no sea `None`.
        - Genera un enlace de configuración (`account_onboarding`) utilizando la API de Stripe, con:
            - `refresh_url`: URL a la que se redirige al usuario en caso de error durante el proceso.
            - `return_url`: URL a la que se redirige al usuario después de completar el proceso.
        - Devuelve la URL generada para que el usuario pueda iniciar el proceso de configuración.

    Returns:
        JsonResponse:
            - `url`: La URL del enlace de configuración si la operación es exitosa.
            - `error`: Un mensaje de error y código de estado 400 o 500 si ocurre un problema.
    """
    try:
        # Decodifica el cuerpo de la solicitud para obtener los datos JSON
        data = json.loads(request.body.decode('utf-8'))
        connected_account_id = data.get('account')
        
        # Verifica que connected_account_id no sea None
        if not connected_account_id:
            return JsonResponse({'error': 'ID de cuenta conectada no proporcionado'}, status=400)

        account_link = stripe.AccountLink.create(
            account=connected_account_id,
            refresh_url=request.build_absolute_uri(reverse('stripe_onboarding_complete')),
            return_url=request.build_absolute_uri(reverse('stripe_onboarding_complete')),
            type="account_onboarding",
        )

        return JsonResponse({'url': account_link.url})
    except Exception as e:
        print(f"Error al crear el enlace de la cuenta conectada: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def stripe_onboarding_complete(request):
    """
    Funcion implementada por Alan
    Completa el proceso de configuración de la cuenta conectada de Stripe.

    Esta función se utiliza como punto de retorno después de que un proveedor completa el proceso de
    configuración de su cuenta conectada de Stripe. Recupera el `stripe_account_id` almacenado en la
    sesión, lo guarda en el perfil del proveedor y limpia la sesión para mantener la seguridad.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente.

    Funcionalidad:
        - Recupera el `stripe_account_id` almacenado en la sesión.
        - Si el `stripe_account_id` está presente:
            - Lo asocia al perfil del proveedor autenticado y lo guarda en la base de datos.
            - Limpia el `stripe_account_id` de la sesión del usuario para mayor seguridad.
        - Redirige al usuario a la página de servicios o a la página especificada.

    Returns:
        HttpResponseRedirect: Redirige al usuario a la vista `servicios_sin_login`.
    """
    # Obtén el `stripe_account_id` de la sesión (o desde la base de datos temporalmente)
    stripe_account_id = request.session.get('stripe_account_id')

    if stripe_account_id:
        # Guarda el `stripe_account_id` en el perfil del proveedor
        request.user.proveedor.stripe_account_id = stripe_account_id
        request.user.proveedor.save()
        # Limpia la sesión para no mantener el `stripe_account_id`
        del request.session['stripe_account_id']

    # Redirige al usuario a la página de servicios o a cualquier otra página deseada
    return redirect('servicios_sin_login')

@login_required
@csrf_exempt
def create_checkout_session(request, solicitud_id):
    """
    Funcion implementada por Alan
    Crea una sesión de pago en Stripe para una solicitud de presupuesto.

    Esta función genera una sesión de pago en Stripe utilizando los detalles de una solicitud de
    presupuesto, como el precio del servicio, el proveedor y la cuenta conectada de Stripe del proveedor.
    Incluye el IVA y aplica una comisión del 10% en el monto total.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado.
        @csrf_exempt: Exime esta vista de la verificación CSRF, ya que interactúa con una API externa.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente.
        solicitud_id (int): El ID de la solicitud de presupuesto para la cual se está creando la sesión de pago.

    Funcionalidad:
        - Obtiene la solicitud de presupuesto, el servicio y el proveedor asociados al `solicitud_id`.
        - Verifica que el proveedor tenga configurada una cuenta conectada de Stripe (`stripe_account_id`).
        - Calcula el precio total del servicio, incluyendo el 8% de IVA.
        - Crea una sesión de pago en Stripe con los siguientes parámetros:
            - Tipo de método de pago: Tarjeta.
            - Detalles del producto: Nombre y precio en centavos.
            - URLs de éxito y cancelación.
            - Comisión del 10% transferida a la cuenta de la plataforma.
            - Metadata que incluye el `solicitud_id` para seguimiento.

    Returns:
        JsonResponse:
            - `id`: El ID de la sesión de pago creada si la operación es exitosa.
            - `error`: Un mensaje de error y código de estado 400 o 500 si ocurre un problema.
    """
    try:
        # Obtener el servicio y el proveedor mediante la Solicitud de Presupuesto
        solicitud = Solicitud_Presupuesto.objects.get(id=solicitud_id)
        servicio = solicitud.servicio
        proveedor = solicitud.proveedor

        if not proveedor.stripe_account_id:
            return JsonResponse({'error': 'El proveedor no tiene una cuenta de Stripe configurada.'}, status=400)
        
        precio_total = solicitud.precio * Decimal('1.08')  # Aplica el 8% de IVA al precio total

        # Crear la sesión de checkout de Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',  # Cambia según la moneda que necesites
                    'product_data': {
                        'name': servicio.nombre,
                    },
                    'unit_amount': int(precio_total * 100),  # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
            payment_intent_data={
                'application_fee_amount': int(precio_total * 10),  # Comisión del 10%
                'transfer_data': {
                    'destination': proveedor.stripe_account_id,
                },
            },
            metadata={'solicitud_id': solicitud_id}  # Agrega el solicitud_id al metadata
        )

        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        print(f"Error al crear la sesión de checkout: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
def payment_success(request):
    """
    Funcion implementada por Alan
    Maneja el flujo posterior a un pago exitoso en Stripe.

    Esta función verifica la sesión de pago de Stripe, procesa los datos relacionados con la transacción,
    y genera las notificaciones correspondientes para el proveedor y el cliente. También asegura que la
    transacción no se procese más de una vez.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Debe contener el parámetro
                               `session_id` en la URL.

    Funcionalidad:
        - Recupera el `session_id` de la solicitud y verifica que no sea nulo.
        - Consulta la sesión de Stripe utilizando el `session_id` para obtener detalles de la transacción.
        - Obtiene la solicitud de presupuesto asociada a la sesión de Stripe mediante su `solicitud_id`.
        - Calcula el precio total del servicio, incluyendo el 8% de IVA.
        - Verifica si la transacción ya ha sido procesada para evitar duplicados.
        - Crea una entrada en la tabla `Contratacion` con los detalles de la transacción.
        - Genera las siguientes notificaciones:
            - Confirmación de pago para el proveedor.
            - Confirmación de pago para el cliente.
            - Solicitud para calificar el servicio para el cliente.
        - Marca como leída la notificación de tipo "Respuesta de Solicitud" asociada a la solicitud.

    Returns:
        HttpResponse:
            - Renderiza la plantilla `payment_success.html` con los detalles de la solicitud si la transacción
              es exitosa o si ya fue procesada anteriormente.
            - Renderiza la plantilla `payment_success.html` con un mensaje de error si no se puede recuperar
              la sesión de Stripe o si el `session_id` es nulo.
    """
    session_id = request.GET.get('session_id')
    if not session_id:
        # Maneja el caso en que no se pase el `session_id`
        return render(request, 'payment_success.html', {'error': 'No se pudo obtener el ID de la sesión.'})
    
    # Recupera la sesión de Stripe para obtener los detalles
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # `metadata` tiene la `solicitud_id` pasada al crear la sesión
        solicitud_id = checkout_session.metadata.get('solicitud_id')
        solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)  # Obtén la solicitud de la base de datos
        
        # Actualiza el precio total con el 8% de IVA
        solicitud.precio_con_iva = solicitud.precio * Decimal('1.08')
        
        # Verifica si ya existe una contratación con este session_id para evitar duplicados
        if Contratacion.objects.filter(stripe_session_id=session_id).exists():
            return render(request, 'payment_success.html', {'solicitud': solicitud, 'message': 'Esta transacción ya fue procesada.'})
        
        #Guarda los datos de la transaccion
        Contratacion.objects.create(
            precio=solicitud.precio_con_iva,
            estado_transaccion='completada',
            fecha_contratacion=datetime.now(),
            cliente=solicitud.cliente,
            servicio=solicitud.servicio,
            stripe_session_id=session_id  # Asocia el session_id
        )
        
        #Crea una notificacion de confirmacion de pago para el proveedor
        Notificacion.objects.create(
            user=solicitud.proveedor.user, 
            solicitud=solicitud,
            tipo_notificacion='Confirmacion de Pago',
            leido=False #Por defecto no leido
        )
        
        #Crea una notificacion de confirmacion de pago para el cliente
        Notificacion.objects.create(
            user=solicitud.cliente.user, 
            solicitud=solicitud,
            tipo_notificacion='Confirmacion de Pago',
            leido=False #Por defecto no leido
        )
        
        #Crea una notificacion para calificar el servicio
        Notificacion.objects.create(
            user=solicitud.cliente.user, 
            solicitud=solicitud,
            tipo_notificacion='Calificar Servicio',
            leido=False #Por defecto no leido
        )
        
        # Marca como leída la notificación de tipo "Respuesta de Solicitud" asociada a la solicitud
        Notificacion.objects.filter(
            solicitud=solicitud,
            tipo_notificacion='Respuesta de Solicitud',
            leido=False
        ).update(leido=True)
        
        return render(request, 'payment_success.html', {
            'solicitud': solicitud
        })
        
    except stripe.error.InvalidRequestError:
        return render(request, 'payment_success.html', {'error': 'Error al recuperar la sesión de pago.'})
    

def payment_cancel(request):    
    """
    Funcion implementada por Alan
    Vista que maneja la cancelación de un pago.

    Esta vista genera el template 'payment_cancel.html' cuando se cancela el proceso de un pago.

    Args:
        request (HttpRequest): El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'payment_cancel.html'.
    """
    return render(request, 'payment_cancel.html')

@login_required
def stripe_dashboard_link(request):
    """
    Funcion implementada por Alan
    Genera un enlace para que el proveedor pueda acceder a su Express Dashboard de Stripe.

    La vista verifica que el usuario sea un proveedor y tenga una cuenta de Stripe asociada. Si se cumple esta
    condición, se genera un enlace de inicio de sesión al Express Dashboard de Stripe y se redirige al proveedor 
    a la URL generada. De lo contrario, se devuelve un error en formato JSON.

    Args:
        request (HttpRequest): El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse:
            - Redirige al proveedor al Express Dashboard de Stripe si se cumple la condición.
            - Devuelve un error en formato JSON si no se cumple la condición o si ocurre un error.
    """
    try:
        # Verifica que el usuario sea un proveedor y tenga una cuenta de Stripe
        if request.user.es_proveedor and request.user.proveedor.stripe_account_id:
            stripe_account_id = request.user.proveedor.stripe_account_id

            # Genera el enlace de inicio de sesión al Express Dashboard
            login_link = stripe.Account.create_login_link(stripe_account_id)
            
            # Redirige al proveedor al Express Dashboard de Stripe
            return redirect(login_link.url)
        else:
            return JsonResponse({'error': 'El usuario no tiene cuenta de Stripe o no es un proveedor'}, status=400)
    except Exception as e:
        print(f"Error al generar el enlace de acceso al dashboard de Stripe: {e}")
        return JsonResponse({'error': 'No se pudo generar el enlace de acceso al dashboard de Stripe.'}, status=500)