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
            # Guardar las imágenes temporalmente
            foto_identificacion = form.cleaned_data['foto_identificacion']
            foto_rostro = form.cleaned_data['foto_rostro']
            identificacion_path = default_storage.save(f'temp/{foto_identificacion.name}', foto_identificacion)
            rostro_path = default_storage.save(f'temp/{foto_rostro.name}', foto_rostro)

            # Leer las imágenes en formato binario para Rekognition
            with default_storage.open(identificacion_path, 'rb') as id_img, default_storage.open(rostro_path, 'rb') as rostro_img:
                identificacion_bytes = id_img.read()
                rostro_bytes = rostro_img.read()
                
            # Comparación de rostros con Rekognition
            try:
                # Llamada a Rekognition para comparar las caras
                response = rekognition_client.compare_faces(
                    SourceImage={'Bytes': identificacion_bytes},
                    TargetImage={'Bytes': rostro_bytes},
                    SimilarityThreshold=90  # Establece el umbral de similitud deseado
                )

                # Verificar si se encontró una coincidencia
                if response['FaceMatches']:
                    # Coincidencia exitosa, continuar con el registro del usuario
                    user = form.save()
                    nombre_completo = form.cleaned_data['nombre_completo']
                    Cliente.objects.create(user=user, nombre_completo=nombre_completo)
                    login(request, user, backend='Usuarios.backends.EmailBackend')
                    return redirect('servicios_sin_login')
                else:
                    form.add_error(None, "Las fotos no coinciden. Verifica que ambas fotos sean claras y correspondan a la misma persona.")
                    
                # Eliminar los archivos temporales después de usarlos
                default_storage.delete(identificacion_path)
                default_storage.delete(rostro_path)
            except Exception as e:
                form.add_error(None, f"Error al procesar las imágenes. Asegúrate de que las fotos sean claras y correspondan a la misma persona. Error")
    else:
        form = RegistroClienteForm()

    return render(request, 'registro_cliente.html', {'form': form})

def registro_proveedor(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            nombre_empresa = form.cleaned_data['nombre_empresa']
            
            # Obtener las fotos cargadas
            foto_identificacion = request.FILES['foto_identificacion']
            foto_rostro = request.FILES['foto_rostro']

            # Leer el contenido de las imágenes para Rekognition
            identificacion_bytes = foto_identificacion.read()
            rostro_bytes = foto_rostro.read()

            # Comparación de rostros con Rekognition
            try:
                response = rekognition_client.compare_faces(
                    SourceImage={'Bytes': identificacion_bytes},
                    TargetImage={'Bytes': rostro_bytes},
                    SimilarityThreshold=90  # Puedes ajustar el umbral de similitud
                )

                # Verificar si se encontró una coincidencia
                if response['FaceMatches']:
                    # Guardar el usuario en la base de datos
                    user = form.save()
                    
                    # Crear el proveedor asociado al usuario
                    Proveedor.objects.create(
                        user=user, 
                        nombre_empresa=nombre_empresa
                    )
                    
                    # Iniciar sesión automáticamente
                    login(request, user, backend='Usuarios.backends.EmailBackend')
                    
                    # Redirigir a la pantalla de servicios
                    return redirect('servicios_sin_login')
                else:
                    form.add_error(None, "La verificación de identidad falló. Asegúrate de que las fotos coincidan.")
            except Exception as e:
                form.add_error(None, f"Error al procesar las imágenes. Asegúrate de que las fotos sean claras y correspondan a la misma persona. Error")
        else:
            return render(request, 'registro_proveedor.html', {'form': form})
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