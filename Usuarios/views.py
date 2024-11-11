import base64
import boto3
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegistroClienteForm, RegistroProveedorForm, InicioSesionForm
from .models import Cliente, Proveedor
from django.contrib.auth import login, logout, authenticate
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile



rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

def inicio(request):
    """Renderiza la página de inicio.

    Esta vista muestra la página principal de la aplicación.

    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'index.html'.
    """
    return render(request, 'index.html')

def acerca_de(request):
    """Renderiza la página 'Acerca de'.

    Esta vista muestra la página 'Acerca de' de la aplicación.

    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'acerca_de.html'.
    """
    return render(request, 'acerca_de.html')

def registro_cliente(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST, request.FILES)
        if form.is_valid():
            # Solo se guarda temporalmente la imagen de la identificación
            foto_identificacion = form.cleaned_data['foto_identificacion']
            foto_rostro_base64 = request.POST.get('foto_rostro')
            identificacion_path = default_storage.save(f'temp/{foto_identificacion.name}', foto_identificacion)
            
            # Convertir la imagen base64 capturada en bytes
            foto_rostro_bytes = None
            if foto_rostro_base64:
                format, imgstr = foto_rostro_base64.split(';base64,')
                foto_rostro_bytes = base64.b64decode(imgstr)

            # Leer la imagen de identificación en formato binario para Rekognition
            with default_storage.open(identificacion_path, 'rb') as id_img:
                identificacion_bytes = id_img.read()
                
            # Comparación de rostros con Rekognition solo si se ha capturado el rostro
            if foto_rostro_bytes:
                try:
                    response = rekognition_client.compare_faces(
                        SourceImage={'Bytes': identificacion_bytes},
                        TargetImage={'Bytes': foto_rostro_bytes},
                        SimilarityThreshold=90
                    )

                    # Verificar si se encontró una coincidencia
                    if response['FaceMatches']:
                        # Guardar el usuario en la base de datos y redirigir
                        user = form.save()
                        nombre_completo = form.cleaned_data['nombre_completo']
                        Cliente.objects.create(user=user, nombre_completo=nombre_completo)
                        login(request, user, backend='Usuarios.backends.EmailBackend')
                        return redirect('servicios_sin_login')
                    else:
                        form.add_error(None, "Las fotos no coinciden. Asegúrate de que ambas fotos correspondan a la misma persona.")
                except Exception as e:
                    form.add_error(None, f"Error en la verificación: {e}")
                finally:
                    # Eliminar los archivos temporales después de usarlos
                    default_storage.delete(identificacion_path)
            else:
                form.add_error(None, "No se capturó una foto para el rostro. Por favor, toma una foto.")
        else:
            form.add_error(None, "Error al procesar el formulario. Asegúrate de que los datos sean correctos.")
    else:
        form = RegistroClienteForm()

    return render(request, 'registro_cliente.html', {'form': form})


def registro_proveedor(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            nombre_empresa = form.cleaned_data['nombre_empresa']
            
            # Solo se guarda temporalmente la imagen de la identificación
            foto_identificacion = form.cleaned_data['foto_identificacion']
            foto_rostro_base64 = request.POST.get('foto_rostro')
            identificacion_path = default_storage.save(f'temp/{foto_identificacion.name}', foto_identificacion)
            
            # Convertir la imagen base64 capturada en bytes
            foto_rostro_bytes = None
            if foto_rostro_base64:
                format, imgstr = foto_rostro_base64.split(';base64,')
                foto_rostro_bytes = base64.b64decode(imgstr)

            # Leer la imagen de identificación en formato binario para Rekognition
            with default_storage.open(identificacion_path, 'rb') as id_img:
                identificacion_bytes = id_img.read()

            # Comparación de rostros con Rekognition solo si se ha capturado el rostro
            if foto_rostro_bytes:
                try:
                    response = rekognition_client.compare_faces(
                        SourceImage={'Bytes': identificacion_bytes},
                        TargetImage={'Bytes': foto_rostro_bytes},
                        SimilarityThreshold=90
                    )

                    # Verificar si se encontró una coincidencia
                    if response['FaceMatches']:
                        # Guardar el usuario en la base de datos y redirigir
                        user = form.save()
                        Proveedor.objects.create(
                            user=user, 
                            nombre_empresa=nombre_empresa, 
                            clabe=form.cleaned_data['clabe']
                        )
                        login(request, user, backend='Usuarios.backends.EmailBackend')
                        return redirect('servicios_sin_login')
                    else:
                        form.add_error(None, "Las fotos no coinciden. Asegúrate de que ambas fotos correspondan a la misma persona.")
                except Exception as e:
                    form.add_error(None, f"Error en la verificación: {e}")
                finally:
                    # Eliminar los archivos temporales después de usarlos
                    default_storage.delete(identificacion_path)
            else:
                form.add_error(None, "No se capturó una foto para el rostro. Por favor, toma una foto.")
        else:
            form.add_error(None, "Error al procesar el formulario. Asegúrate de que los datos sean correctos.")
    else:
        form = RegistroProveedorForm()

    return render(request, 'registro_proveedor.html', {'form': form})


def inicio_sesion(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('servicios_sin_login')
            else:
                form.add_error(None, "Correo o contraseña incorrecta")
    else:
        form = InicioSesionForm()
            
    return render(request, 'inicio_sesion.html', {'form': form})

def cerrar_sesion(request):
    logout(request) #Elimina la cookie de sesion
    return redirect('index')