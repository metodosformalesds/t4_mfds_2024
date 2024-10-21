from django.shortcuts import render, redirect
from .forms import RegistroClienteForm, RegistroProveedorForm, InicioSesionForm
from .models import Cliente, Proveedor
from django.contrib.auth import login, authenticate

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
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            # Obtener el nombre completo
            nombre_completo = form.cleaned_data['nombre_completo']
                
            # Guarda el nuevo usuario en la tabla User
            user = form.save()
            
            # Guarda el nuevo usuario en la tabla User Cliente
            Cliente.objects.create(user=user, nombre_completo=nombre_completo)  # Crea el cliente asociado al usuario
            
            # Inicia sesión automáticamente usando el backend personalizado
            login(request, user, backend='Usuarios.backends.EmailBackend')
            
            # Envia a la pantalla de servicios
            return redirect('servicios_sin_login')
    else: # En el caso contrario seria una solicitud GET en la que solo mostramos la pagina
        form = RegistroClienteForm()
        
    return render(request, 'registro_cliente.html', {'form': form})

def registro_proveedor(request):
    # Si la solicitud es de tipo POST quiere decir que se recibieron datos
    if request.method == 'POST':
        form = RegistroProveedorForm(request.POST)
        if form.is_valid():
            # Obtener el nombre de la empresa
            nombre_empresa = form.cleaned_data['nombre_empresa']
                
            # Guarda el nuevo usuario en la tabla User
            user = form.save() 
            
            # Crear una entrada en la tabla Proveedor
            Proveedor.objects.create(user=user, nombre_empresa=nombre_empresa, clabe=form.cleaned_data['clabe'])  # Crea el proveedor asociado al usuario
            
            # Inicia sesión automáticamente usando el backend personalizado
            login(request, user, backend='Usuarios.backends.EmailBackend')
            
            # Envia a la pantalla de servicios
            return redirect('servicios_sin_login')
    else: # En el caso contrario seria una solicitud GET en la que solo mostramos la pagina
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
