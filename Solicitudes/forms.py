from django import forms
from .models import Solicitud_Presupuesto

class SolicitudPresupuestoClienteForm(forms.ModelForm):
    """
    Formulario para que los clientes soliciten presupuestos de servicios.

    El formulario `SolicitudPresupuestoClienteForm` permite a los clientes completar la información 
    necesaria para solicitar un presupuesto de un servicio. Incluye campos personalizados para 
    detallar la dirección del evento y los datos relevantes para la solicitud, como tipo de evento, 
    fecha, duración y cantidad de asistentes.

    Campos adicionales:
        - `calle`: Calle donde se llevará a cabo el evento (CharField, requerido).
        - `numero_exterior`: Número exterior del domicilio del evento (CharField, requerido).
        - `numero_interior`: Número interior del domicilio del evento (CharField, opcional).
        - `colonia`: Colonia donde se realizará el evento (CharField, requerido).
        - `codigo_postal`: Código postal del domicilio del evento (CharField, requerido).

    Meta:
        - `model`: Asocia este formulario al modelo `Solicitud_Presupuesto`.
        - `fields`: Incluye los campos `tipo_evento`, `fecha`, `duracion`, y `personas`.
        - `widgets`: Personaliza los widgets HTML para cada campo:
            - `tipo_evento`: Dropdown (`Select`) con opciones predefinidas.
            - `fecha`: Campo de entrada con selector de fecha (`DateInput`).
            - `duracion`: Campo numérico (`NumberInput`) para ingresar la duración del evento.
            - `personas`: Campo numérico (`NumberInput`) para especificar el número de asistentes.

    Métodos de limpieza:
        - `clean_personas`: 
            - Valida que la cantidad de personas sea un número entero mayor a cero.
            - Lanza un error de validación si no cumple estas condiciones.
        - `clean_duracion`: 
            - Valida que la duración sea mayor a cero.
            - Lanza un error de validación si no cumple esta condición.
    """
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
        """
        Limpia el campo `personas` para asegurarse de que contenga un número entero mayor a cero.

        Valida que el campo `personas` sea un número entero mayor a cero. Si no cumple esta condición, 
        lanza un error de validación.

        Returns:
            int: El valor de `personas` si es válido, None de lo contrario.
        """
        personas = self.cleaned_data.get('personas')
        if personas is not None and not isinstance(personas, int): #Validar si es un entero
            raise forms.ValidationError("La cantidad de personas debe ser un número entero.")
        if personas <= 0: #Validar si es mayor a cero
            raise forms.ValidationError("La cantidad de personas debe ser mayor a cero.")
        return personas
    
    def clean_duracion(self):
        """
        Valida el campo `duracion` para asegurarse de que sea mayor a cero.

        Este método se llama cuando se limpia el campo `duracion`. 
        Verifica que el valor ingresado sea mayor a cero, y si no lo es, lanza un error de validación.

        Returns:
            float: El valor de `duracion` si es valido, None de lo contrario.
        """
        duracion = self.cleaned_data.get('duracion')
        if duracion <= 0: #Validar si es mayor a cero
            raise forms.ValidationError("La duracion debe ser mayor a cero.")
        return duracion