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
    return render(request, 'payment_cancel.html')

@login_required
def stripe_dashboard_link(request):
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