from django.shortcuts import render

def servicios_sin_login(request):
    return render(request, 'servicios_sin_login.html')
