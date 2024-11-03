from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SolicitudPresupuestoClienteForm
from .models import Solicitud_Presupuesto
from Servicios.models import Servicio
from Usuarios.models import Proveedor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required #Decorado para asegurarse de que el usuario haya iniciado sesión
def solicitar_presupuesto(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)  # Verifica que el servicio exista y lo obtiene
    proveedor = servicio.proveedor

    if request.method == 'POST':
        form = SolicitudPresupuestoClienteForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.cliente = request.user.cliente  # Asigna el id del cliente
            solicitud.proveedor = proveedor # Asigna el id del proveedor
            solicitud.servicio = servicio # Asigna el id del servicio
            solicitud.status = 'pendiente'  # Estado inicial
            # Concatena los datos que conforman la dirección
            solicitud.direccion = f"{form.cleaned_data['calle']}, {form.cleaned_data['numero_exterior']} {form.cleaned_data.get('numero_interior', '')}, {form.cleaned_data['colonia']}, {form.cleaned_data['codigo_postal']}"
            solicitud.save()  # Guarda la solicitud en la base de datos
            
            return JsonResponse({'status': 'success', 'message': 'Solicitud enviada exitosamente'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    
     # Si es un GET, devolvemos el formulario vacío
    form = SolicitudPresupuestoClienteForm()
    return render(request, 'solicitud_presupuesto.html', {'form': form, 'servicio': servicio})