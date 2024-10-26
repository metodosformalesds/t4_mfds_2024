from django import forms
from .models import Servicio, Imagenes_Servicios
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
        fields = ['nombre', 'categoria', 'precio_minimo', 'precio_maximo', 'informacion_detallada']
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
            'precio_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
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