from django import forms
from .models import Servicio, Imagenes_Servicios, Reseña
from django.forms.utils import flatatt

#Formulario para la publicacion de servicios
class PublicarServicioForm(forms.ModelForm):
    calle = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_exterior = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_interior = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})) #Este campo es opcional
    colonia = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    codigo_postal = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Servicio #El modelo de este formulario es Servicio
        fields = ['nombre', 'categoria', 'precio_minimo','informacion_detallada']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(choices=[
                ('Entretenmiento', 'Entretenmiento'), 
                ('Equipamiento_Mobiliario', 'Equipamiento y mobiliario'), 
                ('Espacios_Eventos', 'Espacios para eventos'), 
                ('Catering', 'Catering'), 
                ('Fotografia', 'Fotografía'), 
                ('Decoracion', 'Decoración')], attrs={'class': 'form-select'}),
            'precio_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'informacion_detallada': forms.Textarea(attrs={'class': 'form-control'}),
        }

#Clase personalizada para recibir multiples archivos
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.max_num = kwargs.pop('max_num', None)
        super().__init__(*args, **kwargs)
        self.widget.attrs['multiple'] = True

    def clean(self, data, initial=None):
        return data
        
#Formulario para guardar multiples imagenes
class MultipleImagenesServiciosForm(forms.Form):
    imagen = MultipleFileField(max_num=5)
    
    class Meta:
        model = Imagenes_Servicios
        fields = ['imagen']
        
# codigo para editar publicacion 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Servicio, Imagenes_Servicios
from .forms import PublicarServicioForm, MultipleImagenesServiciosForm

@login_required
def publicar_servicio(request):
    if request.method == 'POST':
        # Procesa el formulario del servicio
        servicio_form = PublicarServicioForm(request.POST)
        imagenes_form = MultipleImagenesServiciosForm(request.FILES or None)
        
        if servicio_form.is_valid() and imagenes_form.is_valid():
            # Guardar el servicio
            servicio = servicio_form.save(commit=False)
            servicio.proveedor = request.user.proveedor  # Asigna el proveedor actual
            servicio.direccion = f"{servicio_form.cleaned_data['calle']} {servicio_form.cleaned_data['numero_exterior']} {servicio_form.cleaned_data.get('numero_interior', '')}, {servicio_form.cleaned_data['colonia']}, {servicio_form.cleaned_data['codigo_postal']}"
            servicio.save()

            # Guardar las imágenes
            for imagen in request.FILES.getlist('imagen'):
                Imagenes_Servicios.objects.create(servicio=servicio, imagen=imagen)

            return redirect('detalle_servicio', servicio_id=servicio.id)  # Redirige a la página de detalles del servicio después de guardar

    else:
        servicio_form = PublicarServicioForm()
        imagenes_form = MultipleImagenesServiciosForm()

    context = {
        'servicio_form': servicio_form,
        'imagenes_form': imagenes_form,
    }
    return render(request, 'publicar_servicio.html', context)

from django import forms
from .models import Reseña

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(choices=[(i, f"{i} estrellas") for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={'rows': 3}),
        }
