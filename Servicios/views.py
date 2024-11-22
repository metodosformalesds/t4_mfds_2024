from django.shortcuts import render, get_object_or_404, redirect
from .forms import PublicarServicioForm, MultipleImagenesServiciosForm
from .models import Imagenes_Servicios, Servicio, Reseña
from Solicitudes.models import Solicitud_Presupuesto
from Notificaciones.models import Notificacion  
from PIL import Image
import os
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .forms import PublicarServicioForm
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from decimal import Decimal
from django.core.paginator import Paginator

@login_required
def perfil(request):
    """
    Funcion implementada por Alan
    Vista para mostrar el perfil del usuario actual.

    Muestra las notificaciones de confirmación de pago del usuario actual, ordenadas de más reciente a más antigua. 
    Cada notificación se acompaña de su precio con IVA.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado para acceder a esta función.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.

    Returns:
        HttpResponse: La respuesta HTTP con el perfil del usuario actual.
    """
    notificaciones = Notificacion.objects.filter(user=request.user, tipo_notificacion='Confirmacion de Pago').order_by('-fecha')
    for notificacion in notificaciones:
        # Calcula el precio con IVA
        notificacion.precio_con_iva = notificacion.solicitud.precio * Decimal('1.08')
    return render(request, 'perfil.html', {
        'notificaciones': notificaciones,
    })

def servicios_sin_login(request):
    """
    Funcion implementada por Luis y Alan
    Vista para mostrar los servicios en la plataforma sin requerir autenticación.

    Muestra todos los servicios en la plataforma, o los servicios que coinciden con la categoría seleccionada 
    mediante el parámetro GET "categoria".

    Si el usuario ha iniciado sesión, se cargan sus notificaciones no leídas, ordenadas de más reciente a más antigua.

    Args:
        request (HttpRequest): El objeto HTTP que contiene los datos de la solicitud.

    Returns:
        HttpResponse: La respuesta HTTP con la lista de servicios en la plataforma.
    """
    # Obtener la categoría seleccionada desde la solicitud GET
    categoria_seleccionada = request.GET.get('categoria')
    
    # Filtrar servicios según la categoría seleccionada o mostrar todos si no se selecciona ninguna
    if categoria_seleccionada and categoria_seleccionada != "Todas las categorias":
        servicios = Servicio.objects.filter(categoria__iexact=categoria_seleccionada)
    else:
        servicios = Servicio.objects.all()
        
        # Configuración de la paginación
        paginator = Paginator(servicios, 18)  # Mostrar 18 servicios por página
        page_number = request.GET.get('page')  # Obtener el número de página desde la URL
        page_obj = paginator.get_page(page_number)  # Obtener la página actual
    
    # Verificar si el usuario ha iniciado sesión y obtener "Mis servicios"
    if request.user.is_authenticated:
        proveedor = request.user.proveedor  # Accede al proveedor asociado al usuario
        mis_servicio = Servicio.objects.filter(proveedor=proveedor)  # Obtén los servicios de ese proveedor
        # Obtener todas las notificaciones del usuario, ordenadas de más reciente a más antigua
        notificaciones = Notificacion.objects.filter(user=request.user, leido=False).order_by('-fecha')
    else:
        mis_servicio = []  # Si no está autenticado, no hay servicios que mostrar
        notificaciones = None  # Si no está autenticado, no se cargan notificaciones
    
    return render(request, 'servicios_sin_login.html', {
        'mis_servicio': mis_servicio,  # Pasa los servicios a la plantilla
        'servicios': page_obj.object_list,
        'notificaciones': notificaciones,
        'categoria_seleccionada': categoria_seleccionada,
        'page_obj': page_obj,  # Objeto de la página para la navegación
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })


def publicar_servicio(request):
    """
    Funcion implementada por Alan
    Vista para la publicación de un nuevo servicio por parte de un proveedor.

    Esta función permite a los proveedores registrar un nuevo servicio en el sistema. Incluye la validación 
    de datos del formulario del servicio, la validación y almacenamiento de imágenes relacionadas, 
    y la generación automática de una dirección en formato URL compatible con Google Maps.

    Funcionalidad:
        - Si la solicitud es de tipo POST:
            - Valida los datos ingresados en el formulario del servicio (`PublicarServicioForm`) y 
              las imágenes enviadas (`MultipleImagenesServiciosForm`).
            - Verifica que se carguen un máximo de 5 imágenes y que todas tengan una extensión válida.
            - Verifica que los archivos cargados sean imágenes válidas.
            - Guarda el servicio en la base de datos y asocia las imágenes al servicio.
            - Redirige al usuario a la vista `servicios_sin_login` tras un registro exitoso.
        - Si la solicitud es de tipo GET:
            - Renderiza el formulario vacío para permitir al usuario registrar un nuevo servicio.

    Validaciones:
        - Máximo 5 imágenes cargadas.
        - Extensiones de imágenes válidas: `jpg`, `jpeg`, `png`, `gif`.
        - Verificación de que los archivos cargados sean imágenes.
        
    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Puede ser de tipo POST o GET.

    Returns:
        HttpResponse: Renderiza el formulario en `publicar_servicio.html` si la solicitud es GET o si hay errores 
        de validación. Redirige a `servicios_sin_login` en caso de éxito.
    """
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        servicio_form = PublicarServicioForm(request.POST)
        imagenes_form = MultipleImagenesServiciosForm(
            request.POST, request.FILES)

        if servicio_form.is_valid() and imagenes_form.is_valid():
            # Guarda el servicio pero no en la base de datos
            nuevo_servicio = servicio_form.save(commit=False)

            # Asigna como proveedor el usuario logueado
            nuevo_servicio.proveedor = request.user.proveedor

            # Concatena los datos que conforman la direccion en formato URL para google maps
            direccion = f"{servicio_form.cleaned_data['calle']}%20{servicio_form.cleaned_data['numero_exterior']}%20{servicio_form.cleaned_data.get('numero_interior', '')},%20{servicio_form.cleaned_data['colonia']},%20{servicio_form.cleaned_data['codigo_postal']}%20Juárez,%20Chih."
            nuevo_servicio.direccion = direccion

            # Obtenemos una lista de los archivos cargados
            imagenes = request.FILES.getlist('imagen')

            # Valida que no sean mas de 5 archivos
            if len(imagenes) > 5:
                return render(request, 'publicar_servicio.html', {
                    'servicio_form': servicio_form,
                    'imagenes_form': imagenes_form,
                    'error': 'No puedes cargar más de 5 imágenes.'
                })
            
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif'] # Extensiones de imagen válidas

            for file in imagenes:
                # Validar la extensión
                extension = os.path.splitext(file.name)[1][1:].lower()
                if extension not in valid_extensions:
                    return render(request, 'publicar_servicio.html', {
                        'servicio_form': servicio_form,
                        'imagenes_form': imagenes_form,
                        'error': f"El archivo {file.name} no tiene una extensión válida. Las extensiones permitidas son: {', '.join(valid_extensions)}"
                    })

                # Verificar si el archivo es realmente una imagen
                try:
                    image = Image.open(file)
                    image.verify()  # Verificar si el archivo realmente es una imagen
                except (IOError, SyntaxError):
                    return render(request, 'publicar_servicio.html', {
                        'servicio_form': servicio_form,
                        'imagenes_form': imagenes_form,
                        'error': f"El archivo {file.name} no es una imagen válida."
                    })
                    
            # Guarda la infromacion del servicio en la base de datos
            nuevo_servicio.save()

            # Guarda todas las imagenes enviadas en la base de datos
            for imagen in imagenes:
                Imagenes_Servicios.objects.create(
                    servicio=nuevo_servicio, imagen=imagen)

            return redirect('servicios_sin_login')
    else:  # En el caso contrario seria una solicitud GET en la que solo mostramos la pagina
        servicio_form = PublicarServicioForm()
        imagenes_form = MultipleImagenesServiciosForm()

    return render(request, 'publicar_servicio.html', {
        'servicio_form': servicio_form,
        'imagenes_form': imagenes_form
    })


@login_required
def publicacion_servicio(request, id):
    """
    Funcion implementada por Alan
    Vista para mostrar los detalles de un servicio publicado.

    Esta función permite a los usuarios visualizar los detalles de un servicio específico,
    incluidas las imágenes asociadas, reseñas, calificación promedio y dirección desglosada.
    También verifica si el usuario actual ya ha calificado el servicio.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente.
        id (int): El ID del servicio que se desea mostrar.

    Funcionalidad:
        - Busca el servicio correspondiente al ID proporcionado.
        - Recupera todas las imágenes relacionadas con el servicio.
        - Obtiene las reseñas relacionadas con el servicio, ordenadas por fecha (más recientes primero).
        - Calcula el promedio de las calificaciones del servicio.
        - Verifica si el usuario actual ya ha dejado una reseña para el servicio.
        - Divide la dirección del servicio en componentes individuales: calle, número exterior,
          número interior, colonia y código postal.

    Returns:
        HttpResponse: Renderiza la plantilla `publicacion_servicio.html` con el siguiente contexto:
            - `servicio`: El objeto del servicio.
            - `imagenes`: Lista de imágenes relacionadas con el servicio.
            - `reseñas`: Lista de reseñas relacionadas con el servicio.
            - `user_has_rated`: Indicador booleano de si el usuario ya calificó el servicio.
            - `direccion`: Diccionario con los componentes desglosados de la dirección.

    Redirecciones:
        - Redirige a `servicios_sin_login` si el servicio no existe.
    """
    try:
        servicio = Servicio.objects.get(id=id)
    except Servicio.DoesNotExist:
        return redirect('servicios_sin_login')

    # Obtener las imágenes relacionadas con el servicio
    imagenes = Imagenes_Servicios.objects.filter(servicio=servicio)

   # Obtener todas las reseñas relacionadas con el servicio
    reseñas = Reseña.objects.filter(servicio=servicio).order_by('-fecha')

    # Calcular el promedio de calificación
    promedio_calificacion = reseñas.aggregate(Avg('calificacion'))['calificacion__avg']
    if promedio_calificacion is None:
        promedio_calificacion = 0  # Si no hay reseñas, muestra 0

    # Verificar si el usuario ha calificado el servicio
    user_has_rated = Reseña.objects.filter(servicio=servicio, usuario=request.user).exists()

    # Renderizar la plantilla con el contexto adecuado
    return render(request, 'publicacion_servicio.html', {
        'servicio': servicio,
        'imagenes': imagenes,
        'reseñas': reseñas,
        'user_has_rated': user_has_rated,
        'direccion': {
            'calle': servicio.direccion.split("%20")[0],
            'numero_exterior': servicio.direccion.split("%20")[1],
            'numero_interior': servicio.direccion.split("%20")[2] if " " in servicio.direccion.split("%20")[2] else " ",
            'colonia': servicio.direccion.split("%20")[3],
            'codigo_postal': servicio.direccion.split("%20")[4],
        },
    })

def eliminar_publicacion(request, id):
    """
    Funcion implementada por Alan
    Vista para eliminar una publicación de servicio.

    Recibe como parámetro el `id` del servicio a eliminar.

    Primero, intenta obtener el objeto del servicio con el `id` proporcionado.
    Si no se encuentra, redirige a `servicios_sin_login`.

    Luego, obtiene todas las imágenes relacionadas con el servicio y las elimina
    físicamente de la carpeta `media` y de la base de datos.

    Finalmente, elimina el servicio de la base de datos y redirige a
    `servicios_sin_login`.
    
    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente.
        id (int): El ID del servicio que se desea mostrar.

    Returns:
        HttpResponse: Redirige a `servicios_sin_login` si el servicio se elimina correctamente.
    """
    try:
        servicio = Servicio.objects.get(id=id)
    except Servicio.DoesNotExist:
        return redirect('servicios_sin_login')  # Redirige si no se encuentra el servicio

    imagenes = Imagenes_Servicios.objects.filter(servicio=servicio)
    
    if request.method == 'POST':
        
        for imagen in imagenes: #Recorre todas las imagenes del servicio
            if imagen.imagen and os.path.isfile(imagen.imagen.path):
                os.remove(imagen.imagen.path) #Elimina la imagen de la carpeta media
            imagen.delete() #Elimina la imagen de la base de datos
            
        servicio.delete() # Elimina el servicio de la base de datos
        return redirect('servicios_sin_login')
    
    
# Código para editar publicación
def editar_servicio(request, servicio_id):
    """
    Vista para editar la publicación de un servicio.

    Esta función permite a los proveedores actualizar los datos de un servicio existente, incluidas
    las imágenes asociadas y los detalles de la dirección. También realiza validaciones de los datos
    enviados y de las nuevas imágenes cargadas.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Puede ser de tipo POST para
        actualizar los datos o GET para obtener el servicio a editar.
        servicio_id (int): El ID del servicio que se desea editar.

    Funcionalidad:
        - Recupera el servicio utilizando el ID proporcionado.
        - Si la solicitud es de tipo POST:
            - Valida los datos enviados mediante `PublicarServicioForm`.
            - Actualiza los datos del servicio, incluidas las imágenes asociadas.
            - Construye una nueva dirección en formato URL para Google Maps.
            - Valida las imágenes cargadas (máximo 5 imágenes, extensiones válidas, y archivos que sean imágenes).
            - Guarda los cambios en la base de datos.
            - Devuelve una respuesta JSON con el estado de éxito o los errores de validación.
        - Si la solicitud no es POST, no se realiza ninguna acción específica en esta función.

    Validaciones:
        - Se valida que no se carguen más de 5 imágenes.
        - Solo se permiten extensiones de imágenes válidas (`jpg`, `jpeg`, `png`, `gif`, `bmp`, `webp`).
        - Se verifica que los archivos cargados sean imágenes válidas.

    Returns:
        JsonResponse: Una respuesta JSON con el estado del proceso:
            - `success: True` si el servicio se actualizó correctamente.
            - `success: False` y detalles de errores si hubo problemas con los datos enviados.
    """
    servicio = get_object_or_404(Servicio, id=servicio_id)
    
    if request.method == 'POST':
        form = PublicarServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            servicio = form.save(commit=False)

            # Actualiza la dirección
            servicio.calle = request.POST.get('calle')
            servicio.numero_exterior = request.POST.get('numero_exterior')
            servicio.numero_interior = request.POST.get('numero_interior')
            servicio.colonia = request.POST.get('colonia')
            servicio.codigo_postal = request.POST.get('codigo_postal')

            # Construye la nueva dirección en formato URL para Google Maps
            direccion = f"{servicio.calle}%20{servicio.numero_exterior}%20{servicio.numero_interior},%20{servicio.colonia},%20{servicio.codigo_postal}%20Ciudad%20Juárez,%20Chih."
            servicio.direccion = direccion

            # Procesa las nuevas imágenes si se cargaron
            nuevas_imagenes = request.FILES.getlist('serviceImage')
            if nuevas_imagenes:
                # Valida que no sean más de 5 archivos
                if len(nuevas_imagenes) > 5:
                    return JsonResponse({'success': False, 'error': 'No puedes cargar más de 5 imágenes.'})

                # Extensiones de imagen válidas
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
                for file in nuevas_imagenes:
                    # Validar la extensión
                    extension = os.path.splitext(file.name)[1][1:].lower()
                    if extension not in valid_extensions:
                        return JsonResponse({
                            'success': False, 
                            'error': f"El archivo {file.name} no tiene una extensión válida. Las extensiones permitidas son: {', '.join(valid_extensions)}"
                        })

                    # Verificar si el archivo es realmente una imagen
                    try:
                        image = Image.open(file)
                        image.verify()  # Verificar si el archivo realmente es una imagen
                    except (IOError, SyntaxError):
                        return JsonResponse({
                            'success': False, 
                            'error': f"El archivo {file.name} no es una imagen válida."
                        })
                
                # Borra las imágenes antiguas
                Imagenes_Servicios.objects.filter(servicio=servicio).delete()
                
                # Guarda las nuevas imágenes
                for imagen in nuevas_imagenes:
                    Imagenes_Servicios.objects.create(servicio=servicio, imagen=imagen)

            # Guarda los cambios en el servicio
            servicio.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

@login_required
def agregar_reseña(request, solicitud_id):
    """
    Vista para agregar una reseña de un servicio.

    Esta función permite a los usuarios calificar y comentar un servicio que han contratado previamente.
    La reseña se crea vinculada a la solicitud de presupuesto correspondiente y se actualiza el promedio
    de calificación del servicio.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Debe ser de tipo POST y contener
        los datos de la reseña en formato JSON.
        solicitud_id (int): El ID de la solicitud de presupuesto asociada al servicio que se desea calificar.

    Funcionalidad:
        - Valida que la solicitud sea de tipo POST.
        - Obtiene y parsea el cuerpo de la solicitud en formato JSON.
        - Recupera la solicitud de presupuesto correspondiente al ID proporcionado.
        - Crea una nueva reseña con la calificación y el comentario proporcionados.
        - Calcula y actualiza el promedio de calificación del servicio asociado.
        - Marca como leída la notificación de tipo "Calificar Servicio" asociada a la solicitud.
        - Devuelve una respuesta JSON con los detalles de la reseña creada en caso de éxito.

    Returns:
        JsonResponse:
            - `status: success` con los detalles de la reseña si se crea correctamente.
            - `error` con el mensaje de error y código de estado correspondiente si ocurre un problema.
            - `error` con el mensaje "Método no permitido" si la solicitud no es de tipo POST.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calificacion = int(data.get('ratingStars'))
            comentario = data.get('comment', '')

            # Obtener la solicitud
            solicitud = get_object_or_404(Solicitud_Presupuesto, id=solicitud_id)

            # Crear la reseña
            reseña = Reseña.objects.create(
                servicio=solicitud.servicio,
                usuario=request.user,
                calificacion=calificacion,
                comentario=comentario
            )
            
            # Actualizar el promedio de calificación del servicio
            promedio = Reseña.objects.filter(servicio=solicitud.servicio).aggregate(Avg('calificacion'))['calificacion__avg'] or 0
            solicitud.servicio.promedio_calificacion = promedio
            solicitud.servicio.save()
            
            # Marca como leída la notificación de tipo "Calificar Servicio" asociada a la solicitud
            Notificacion.objects.filter(
                solicitud=solicitud,
                tipo_notificacion='Calificar Servicio',
                leido=False
            ).update(leido=True)

            # Respuesta exitosa con detalles de la reseña
            return JsonResponse({
                'status': 'success',
                'usuario': request.user.email,
                'fecha': reseña.fecha.strftime('%d/%m/%Y'),
                'calificacion': reseña.calificacion,
                'comentario': reseña.comentario,
            }, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

