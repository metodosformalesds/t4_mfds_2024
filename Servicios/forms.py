from django import forms
from .models import Servicio, Imagenes_Servicios, Reseña
from django.forms.utils import flatatt

#Formulario para la publicacion de servicios
class PublicarServicioForm(forms.ModelForm):
    """
    Clase implementada por Alan
    Formulario para la publicación de servicios.

    Este formulario permite a los proveedores registrar nuevos servicios en la plataforma. Incluye campos
    específicos para los datos del servicio, como nombre, categoría, precio mínimo, y descripción, así
    como campos adicionales para capturar la dirección completa.

    Campos adicionales:
        - `calle` (CharField): Campo para ingresar la calle del servicio.
        - `numero_exterior` (CharField): Campo para ingresar el número exterior del servicio.
        - `numero_interior` (CharField): Campo opcional para el número interior del servicio.
        - `colonia` (CharField): Campo para ingresar la colonia del servicio.
        - `codigo_postal` (CharField): Campo para ingresar el código postal del servicio.

    Campos del modelo (`Servicio`):
        - `nombre` (CharField): Nombre del servicio.
        - `categoria` (CharField): Categoría del servicio. Opciones disponibles:
            - Entretenimiento
            - Equipamiento y mobiliario
            - Espacios para eventos
            - Catering
            - Fotografía
            - Decoración
            - Otro
        - `precio_minimo` (DecimalField): Precio mínimo del servicio.
        - `informacion_detallada` (TextField): Descripción detallada del servicio.

    Widgets personalizados:
        - `nombre`: Input de texto con la clase CSS `form-control`.
        - `categoria`: Selector de opciones (`form-select`) con categorías predefinidas.
        - `precio_minimo`: Input numérico con la clase CSS `form-control`.
        - `informacion_detallada`: Área de texto con la clase CSS `form-control`.

    Meta:
        - `model`: Relaciona el formulario con el modelo `Servicio`.
        - `fields`: Especifica los campos del modelo que estarán disponibles en el formulario.

    """
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
                ('Decoracion', 'Decoración'),
                ('Otro', 'Otro'),], attrs={'class': 'form-select'}),
            'precio_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'informacion_detallada': forms.Textarea(attrs={'class': 'form-control'}),
        }

#Clase personalizada para recibir multiples archivos
class MultipleFileField(forms.FileField):
    """
    Clase implementada por Alan
    Campo personalizado para manejar la carga de múltiples archivos.

    Esta clase extiende `forms.FileField` para permitir la selección y carga de múltiples
    archivos a través de un único campo en el formulario. Además, incluye la opción de
    establecer un número máximo de archivos permitidos.

    Atributos:
        max_num (int, opcional): Número máximo de archivos que se pueden cargar. Si no se
                                 proporciona, no hay límite.

    Métodos:
        __init__(*args, **kwargs):
            Inicializa el campo con atributos personalizados, como el soporte para múltiples
            archivos a través del atributo HTML `multiple`.

        clean(data, initial=None):
            Valida los datos proporcionados para este campo. En este caso, simplemente retorna
            los datos sin realizar validaciones adicionales.
    """
    def __init__(self, *args, **kwargs):
        self.max_num = kwargs.pop('max_num', None)
        super().__init__(*args, **kwargs)
        self.widget.attrs['multiple'] = True

    def clean(self, data, initial=None):
        """
        Valida los datos proporcionados para este campo.

        Args:
            data: Archivos cargados por el usuario.
            initial: Valor inicial del campo, si aplica.

        Returns:
            data: Retorna los datos sin aplicar validaciones adicionales.
        """
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
    """
    Funcion implementada por Alan
    Vista para la publicación de un nuevo servicio.

    Esta función permite a los proveedores crear y publicar un nuevo servicio en la plataforma,
    incluyendo información detallada, dirección y las imágenes asociadas.

    Decoradores:
        @login_required: Requiere que el usuario esté autenticado y sea un proveedor.

    Args:
        request (HttpRequest): La solicitud HTTP enviada por el cliente. Puede ser de tipo POST para
                               guardar los datos del servicio, o GET para mostrar el formulario vacío.

    Funcionalidad:
        - Si la solicitud es de tipo POST:
            - Procesa el formulario de servicio (`PublicarServicioForm`) y el formulario de imágenes
              (`MultipleImagenesServiciosForm`).
            - Valida ambos formularios.
            - Guarda el servicio con los datos proporcionados y asigna el proveedor actual.
            - Guarda las imágenes cargadas asociándolas al servicio.
            - Redirige a la página de detalles del servicio después de guardar.
        - Si la solicitud no es de tipo POST (GET):
            - Muestra el formulario vacío para que el usuario pueda ingresar los datos del servicio.

    Returns:
        HttpResponse:
            - Si la solicitud es GET, renderiza la plantilla `publicar_servicio.html` con los formularios.
            - Si la solicitud es POST y los datos son válidos, redirige a la vista `detalle_servicio` con
              el ID del servicio recién creado.

    Contexto:
        - `servicio_form`: El formulario para ingresar los datos del servicio.
        - `imagenes_form`: El formulario para cargar imágenes relacionadas con el servicio.
    """
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
    """
    Formulario para agregar o editar una reseña.

    Este formulario permite a los usuarios ingresar una calificación y un comentario para un servicio.
    Está vinculado al modelo `Reseña` y personaliza los widgets para los campos.

    Meta:
        model (Reseña): Modelo relacionado al formulario.
        fields (list): Campos disponibles en el formulario, que incluyen:
            - `calificacion`: La calificación otorgada al servicio, seleccionada de un menú desplegable.
            - `comentario`: Comentario opcional sobre el servicio.
        widgets (dict): Configuración de widgets personalizados para los campos:
            - `calificacion`: Selector desplegable con opciones de 1 a 5 estrellas.
            - `comentario`: Área de texto con 3 filas predeterminadas.
    """
    class Meta:
        model = Reseña
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(choices=[(i, f"{i} estrellas") for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={'rows': 3}),
        }
