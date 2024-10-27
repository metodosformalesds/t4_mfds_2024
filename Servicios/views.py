from django.shortcuts import render, redirect
from .forms import PublicarServicioForm, MultipleImagenesServiciosForm
from .models import Imagenes_Servicios, Servicio
from PIL import Image
import os

def servicios_sin_login(request):
    # Obtener todos los servicios de la base de datos
    print("Template cargado correctamente")
    servicios = Servicio.objects.all()
    return render(request, 'servicios_sin_login.html', {'servicios': servicios})


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


def publicacion_servicio(request, id):
    try:
        servicio = Servicio.objects.get(id=id)
    except Servicio.DoesNotExist:
        return redirect('servicios_sin_login')  # Redirige o muestra una página de error si no se encuentra el servicio

    imagenes = Imagenes_Servicios.objects.filter(servicio=servicio)
    
    return render(request, 'publicacion_servicio.html', {'servicio': servicio, 'imagenes': imagenes})