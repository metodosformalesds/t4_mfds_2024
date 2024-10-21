from django.shortcuts import render, redirect
from .forms import RegistroClienteForm
from .models import Cliente
from django.contrib.auth import login
import uuid

def inicio(request):
    return render(request, 'index.html')

def acerca_de(request):
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
            user = form.save(commit=False)
            user.username = username
            user = form.save()
            
            # Crear una entrada en la tabla Cliente
            Cliente.objects.create(user=user)  # Crea el cliente asociado al usuario
            
            # Inicia sesion automaticamente
            login(request, user) 
            # Envia a la pantalla de servicios
            return redirect('servicios_sin_login')
    else: # En el caso contrario seria una solicitud GET en la que solo mostramos la pagina
        form = RegistroClienteForm()
        
    return render(request, 'registro_cliente.html', {'form': form})

def registro_proveedor(request):
    return render(request, 'registro_proveedor.html')

def inicio_sesion(request):
    return render(request, 'inicio_sesion.html')

def publicar_servicio(request):
    return render(request, 'publicar_servicio.html')