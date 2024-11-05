from django import forms
from .models import Solicitud_Presupuesto

class SolicitudPresupuestoClienteForm(forms.ModelForm):
    calle = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_exterior = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_interior = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})) #Este campo es opcional
    colonia = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    codigo_postal = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Solicitud_Presupuesto
        fields = ['tipo_evento', 'fecha', 'duracion', 'personas']
        widgets = {
            'tipo_evento': forms.Select(choices=[
                ('Cumpleaños', 'Cumpleaños'), 
                ('Quinceañera', 'Quinceañera'), 
                ('Boda', 'Boda'), 
                ('Aniversario', 'Aniversario'), 
                ('Graduación', 'Graduación'),
                ('Reunión', 'Reunión'),
                ('Corporativo', 'Corporativo'), 
                ('Otro', 'Otro')], attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'duracion' : forms.NumberInput(attrs={'class': 'form-control'}),
            'personas' : forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    def clean_personas(self):
        personas = self.cleaned_data.get('personas')
        if personas is not None and not isinstance(personas, int): #Validar si es un entero
            raise forms.ValidationError("La cantidad de personas debe ser un número entero.")
        if personas <= 0: #Validar si es mayor a cero
            raise forms.ValidationError("La cantidad de personas debe ser mayor a cero.")
        return personas
    
    def clean_duracion(self):
        duracion = self.cleaned_data.get('duracion')
        if duracion <= 0: #Validar si es mayor a cero
            raise forms.ValidationError("La duracion debe ser mayor a cero.")
        return duracion