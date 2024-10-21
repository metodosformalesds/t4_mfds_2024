from django.shortcuts import render, redirect
from .forms import RegistroClienteForm, RegistroProveedorForm
from .models import Cliente, Proveedor
from django.contrib.auth import login
import uuid

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
            # Crear un nombre de usuario único
            username = f"{nombre_completo.replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
                
            # Guarda el nuevo usuario en la tabla User
            user = form.save(commit=False) #Se crea la entrada pero no se confirma
            user.username = username #Asigna el nombre de usuario
            user.save() # Se confirma la nueva entrada
            
            # Crear una entrada en la tabla Cliente
            Cliente.objects.create(user=user, nombre_completo=nombre_completo)  # Crea el cliente asociado al usuario
            
            # Inicia sesion automaticamente
            login(request, user) 
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
            # Crear un nombre de usuario único
            username = f"{nombre_empresa.replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
                
            # Guarda el nuevo usuario en la tabla User
            user = form.save(commit=False) #Se crea la entrada pero no se confirma
            user.username = username #Asigna el nombre de usuario
            user.save() # Se confirma la nueva entrada
            
            # Crear una entrada en la tabla Proveedor
            Proveedor.objects.create(user=user, nombre_empresa=nombre_empresa, clabe=form.cleaned_data['clabe'])  # Crea el proveedor asociado al usuario
            
            # Inicia sesion automaticamente
            login(request, user) 
            # Envia a la pantalla de servicios
            return redirect('servicios_sin_login')
    else: # En el caso contrario seria una solicitud GET en la que solo mostramos la pagina
        form = RegistroProveedorForm()
        
    return render(request, 'registro_proveedor.html', {'form': form})

def inicio_sesion(request):
    return render(request, 'inicio_sesion.html')
