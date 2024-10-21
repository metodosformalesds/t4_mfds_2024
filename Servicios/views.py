from django.shortcuts import render

def servicios_sin_login(request):
    return render(request, 'servicios_sin_login.html')

def publicar_servicio(request):
    return render(request, 'publicar_servicio.html')

def publicacion_servicio(request):
    return render(request, 'publicacion_servicio.html')
