from django.shortcuts import render, get_object_or_404, redirect
from .forms import PublicarServicioForm, MultipleImagenesServiciosForm
from .models import Imagenes_Servicios, Servicio, Reseña
from Notificaciones.models import Notificacion  
from PIL import Image
import os
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import PublicarServicioForm
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
import json



def service_list(request):
    categoria_seleccionada = request.GET.get('categoria')  # Captura la categoría seleccionada de la URL
    
    # Obtén todos los servicios
    services = Servicio.objects.all()

    # Filtra los servicios por categoría si se selecciona una
    if categoria_seleccionada:
        services = services.filter(categoria=categoria_seleccionada)

    # Obtén todas las categorías únicas para el combobox
    categorias = Servicio.objects.values_list('categoria', flat=True).distinct()

    return render(request, 'service_list.html', {
        'servicios': services,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada
    })


def servicios_sin_login(request):
    # Obtener todos los servicios de la base de datos
    servicios = Servicio.objects.all()
    
    # Verificar si el usuario ha iniciado sesión
    if request.user.is_authenticated:
        # Obtener todas las notificaciones del usuario
        notificaciones = Notificacion.objects.filter(user=request.user, leido=False)
    else:
        # Si no está autenticado, no se cargan notificaciones
        notificaciones = None
    
    return render(request, 'servicios_sin_login.html', {
        'servicios': servicios,
        'notificaciones': notificaciones
    })


def publicar_servicio(request):
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

    # Imprimir los nombres de usuario en la consola para verificar
    for reseña in reseñas:
        print(f"Usuario: {reseña.usuario.username if reseña.usuario else 'Sin usuario'}")  # Esto imprimirá el nombre de usuario o indicará si está vacío

    # Renderizar la plantilla con el contexto adecuado
    return render(request, 'publicacion_servicio.html', {
        'servicio': servicio,
        'imagenes': imagenes,
        'reseñas': reseñas,
        'user_has_rated': user_has_rated,
    })

def eliminar_publicacion(request, id):
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
        
        
@csrf_exempt
@login_required
def agregar_reseña(request, servicio_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calificacion = int(data.get('ratingStars'))
            comentario = data.get('comment', '')

            # Obtener el servicio
            servicio = Servicio.objects.get(id=servicio_id)

            # Verificar si el usuario ya ha calificado este servicio
            if Reseña.objects.filter(servicio=servicio, usuario=request.user).exists():
                return JsonResponse({'error': 'Ya has calificado este servicio'}, status=400)

            # Crear la reseña
            reseña = Reseña.objects.create(
                servicio=servicio,
                usuario=request.user,
                calificacion=calificacion,
                comentario=comentario
            )

            # Respuesta exitosa con detalles de la reseña
            return JsonResponse({
                'usuario': request.user.username,
                'fecha': reseña.fecha.strftime('%d/%m/%Y'),
                'calificacion': reseña.calificacion,
                'comentario': reseña.comentario,
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def actualizar_promedio_resena(servicio):
    promedio = Reseña.objects.filter(servicio=servicio).aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    servicio.promedio_calificacion = promedio
    servicio.save()
