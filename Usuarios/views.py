import base64
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.storage import default_storage
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from .forms import RegistroClienteForm, RegistroProveedorForm, InicioSesionForm
from .models import Cliente, Proveedor
import json
from uuid import uuid4
from botocore.exceptions import ClientError
import boto3

rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

# Configuración de ngrok
NGROK_URL = settings.NGROK_URL if hasattr(settings, 'https://4d4b-189-248-73-167.ngrok-free.app') else None


def inicio(request):
    """Renderiza la página de inicio."""
    return render(request, 'index.html')


def acerca_de(request):
    """
    Renderiza la página de 'Acerca de'.

    Esta vista muestra información sobre la aplicación y su propósito.

    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'acerca_de.html'.
    """
    return render(request, 'acerca_de.html')


def comparar_rostros(identificacion_bytes, foto_rostro_bytes):
    """Función centralizada para comparar rostros usando Rekognition."""
    try:
        response = rekognition_client.compare_faces(
            SourceImage={'Bytes': identificacion_bytes},
            TargetImage={'Bytes': foto_rostro_bytes},
            SimilarityThreshold=90
        )
        return response['FaceMatches']
    except ClientError as e:
        raise RuntimeError(f"Error de AWS Rekognition: {e.response['Error']['Message']}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado: {str(e)}")


def registro_cliente(request):
        
    """
    Vista para registrar un cliente.

    Esta vista renderiza el formulario de registro para un cliente. Si se envía el formulario con datos válidos, se
    verifica si las fotos de la identificación y el rostro coinciden. Si coinciden, se guarda el usuario en la base de datos y se redirige a la página de servicios.

    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'registro_cliente.html' con el formulario de registro.
    """

    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST, request.FILES)
        foto_rostro_bytes = None

        # Verificar que el token exista en la sesión
        qr_token = request.session.get('qr_token')
        if not qr_token:
            form.add_error(None, "No se pudo validar la sesión. Intenta nuevamente.")
            return render(request, 'registro_cliente.html', {'form': form})

        print("Valor recibido en foto_rostro:", request.POST.get('foto_rostro'))

        # Procesar imagen capturada en base64
        foto_rostro_base64 = request.POST.get('foto_rostro')
        if foto_rostro_base64:
            try:
                _, imgstr = foto_rostro_base64.split(';base64,')
                foto_rostro_bytes = base64.b64decode(imgstr)
            except Exception as e:
                form.add_error(None, f"Error al procesar la imagen capturada: {e}")
        else:
            form.add_error(None, "No se capturó una foto para el rostro.")

        if form.is_valid():
            # Guardar imagen de identificación de forma temporal
            foto_identificacion = form.cleaned_data['foto_identificacion']
            identificacion_path = default_storage.save(f'temp/{uuid4().hex}_{foto_identificacion.name}', foto_identificacion)

            # Leer imágenes y realizar comparación
            with default_storage.open(identificacion_path, 'rb') as id_img:
                identificacion_bytes = id_img.read()

            if foto_rostro_bytes:
                try:
                    coincidencias = comparar_rostros(identificacion_bytes, foto_rostro_bytes)
                    if coincidencias:
                        user = form.save()
                        Cliente.objects.create(user=user, nombre_completo=form.cleaned_data['nombre_completo'])
                        login(request, user, backend='Usuarios.backends.EmailBackend')
                        return redirect('servicios_sin_login')
                    else:
                        form.add_error(None, "Las fotos no coinciden. Asegúrate de que ambas fotos correspondan a la misma persona.")
                except RuntimeError as e:
                    form.add_error(None, str(e))
                finally:
                    default_storage.delete(identificacion_path)
            else:
                form.add_error(None, "No se capturó una foto para el rostro.")
    else:
        form = RegistroClienteForm()
        qr_token = str(uuid4())  # Genera un token único
        request.session['qr_token'] = qr_token  # Guarda el token en la sesión
        qr_url = request.build_absolute_uri(f"{reverse('captura_bio')}?token={qr_token}")  # URL del QR
        return render(request, 'registro_cliente.html', {'form': form, 'qr_url': qr_url, 'qr_token': qr_token})


def registro_proveedor(request):
    """
    Vista para registrar un proveedor de servicios.

    Esta vista renderiza el formulario de registro para un proveedor. Si se envía el formulario con datos válidos, se
    verifica si las fotos de la identificación y el rostro coinciden. Si coinciden, se guarda el usuario en la base de datos y se redirige a la página de servicios.

    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'registro_proveedor.html' con el formulario de registro.
    """
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroProveedorForm(request.POST, request.FILES)
        foto_rostro_bytes = None

        # Verificar que el token exista en la sesión
        qr_token = request.session.get('qr_token')
        if not qr_token:
            form.add_error(None, "No se pudo validar la sesión. Intenta nuevamente.")
            return render(request, 'registro_proveedor.html', {'form': form})

        # Procesar imagen capturada en base64
        foto_rostro_base64 = request.POST.get('foto_rostro')
        if foto_rostro_base64:
            try:
                _, imgstr = foto_rostro_base64.split(';base64,')
                foto_rostro_bytes = base64.b64decode(imgstr)
            except Exception as e:
                form.add_error(None, f"Error al procesar la imagen capturada: {e}")
        else:
            form.add_error(None, "No se capturó una foto para el rostro.")

        if form.is_valid():
            # Guardar imagen de identificación de forma temporal
            foto_identificacion = form.cleaned_data['foto_identificacion']
            identificacion_path = default_storage.save(f'temp/{uuid4().hex}_{foto_identificacion.name}', foto_identificacion)

            # Leer imágenes y realizar comparación
            with default_storage.open(identificacion_path, 'rb') as id_img:
                identificacion_bytes = id_img.read()

            if foto_rostro_bytes:
                try:
                    coincidencias = comparar_rostros(identificacion_bytes, foto_rostro_bytes)
                    if coincidencias:
                        user = form.save()
                        Proveedor.objects.create(user=user, nombre_empresa=form.cleaned_data['nombre_empresa'])
                        login(request, user, backend='Usuarios.backends.EmailBackend')
                        return redirect('servicios_sin_login')
                    else:
                        form.add_error(None, "Las fotos no coinciden. Asegúrate de que ambas fotos correspondan a la misma persona.")
                except RuntimeError as e:
                    form.add_error(None, str(e))
                finally:
                    default_storage.delete(identificacion_path)
            else:
                form.add_error(None, "No se capturó una foto para el rostro.")
    else:
        form = RegistroProveedorForm()
        qr_token = str(uuid4())  # Genera un token único
        request.session['qr_token'] = qr_token  # Guarda el token en la sesión
        qr_url = request.build_absolute_uri(f"{reverse('captura_bio')}?token={qr_token}")  # URL del QR
        return render(request, 'registro_proveedor.html', {'form': form, 'qr_url': qr_url, 'qr_token': qr_token})

def captura_bio(request):
    """Renderiza la página para capturar la biometría."""
    return render(request, 'captura_bio.html')

@csrf_exempt
def get_temp_image(request):
    token = request.GET.get('token') or request.session.get('qr_token')

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            if image_data and ';base64,' in image_data:
                # Decodificar y guardar la imagen
                _, imgstr = image_data.split(';base64,')
                img_data = ContentFile(base64.b64decode(imgstr), name=f"temp_foto_rostro_{token}.png")
                file_path = default_storage.save(f"temp/{img_data.name}", img_data)

                print(f"[DEBUG] Imagen guardada correctamente: {file_path}")  # Log para confirmar el guardado
                return JsonResponse({"success": True, "message": "Imagen guardada temporalmente."})
            else:
                print("[DEBUG] Formato de imagen inválido en el POST.")
                return JsonResponse({"success": False, "message": "El formato de la imagen es inválido."})
        except Exception as e:
            print(f"[DEBUG] Error al procesar el POST en /get_temp_image/: {e}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    elif request.method == "GET":
        # Recuperar la imagen con el token
        if token:
            file_path = f"temp/temp_foto_rostro_{token}.png"
            print(f"[DEBUG] Intentando recuperar la imagen desde: {file_path}")
            if default_storage.exists(file_path):
                with default_storage.open(file_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                    print(f"[DEBUG] Imagen recuperada correctamente: {file_path}")
                    return JsonResponse({"success": True, "image_base64": f"data:image/png;base64,{image_data}"})
            print("[DEBUG] Imagen no encontrada en el almacenamiento.")
        return JsonResponse({"success": False, "message": "No se encontró una imagen temporal."})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)


def inicio_sesion(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    """
    Vista para el inicio de sesión.

    Si la solicitud es de tipo POST se procesa el formulario de inicio de sesión.
    Si el formulario es válido se autentica al usuario y se redirige a la página de
    servicios. Si el formulario no es válido se agrega un mensaje de error y
    se vuelve a renderizar el formulario.
    Si la solicitud no es de tipo POST se renderiza el formulario vacío.
    
    Args:
        request: El objeto HttpRequest que contiene la información de la solicitud.

    Returns:
        HttpResponse: La respuesta que renderiza el template 'inicio_sesion.html' con el formulario de inicio de sesion. 
    """
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
    """
    Vista para cerrar la sesion del usuario actual.

    Cierra la sesion del usuario actual y redirige a la pagina de inicio.

    Args:
        request: El objeto HttpRequest que contiene la informacion de la solicitud.

    Returns:
        HttpResponse: La respuesta que redirige a la pagina de inicio.
    """
    logout(request) #Elimina la cookie de sesion
    return redirect('index')
