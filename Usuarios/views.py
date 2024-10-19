from django.shortcuts import render

def servicios_sin_login(request):
    return render(request, 'Template/servicios_sin_login.html')  

def inicio(request):
    return render(request, 'index.html')

def acerca_de(request):
    return render(request, 'acerca_de.html')

def registro_cliente(request):
    return render(request, 'registro_cliente.html')

def registro_proveedor(request):
    return render(request, 'registro_proveedor.html')

def inicio_sesion(request):
    return render(request, 'inicio_sesion.html')

def publicar_servicio(request):
    return render(request, 'publicar_servicio.html')