from django import forms
from .models import Encuesta, CamposAdicionales, TipoIncidencia
from departamentos.models import Departamento
from django.forms import inlineformset_factory

# --- FORMULARIO PRINCIPAL DE LA ENCUESTA ---
class EncuestaForm(forms.ModelForm):
    
    tipo_incidencia = forms.ModelChoiceField(
        queryset=TipoIncidencia.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Seleccione un tipo de incidencia",
        label="Tipo de incidencia"
    )
    class Meta:
        model = Encuesta
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- FORMULARIO PARA LOS CAMPOS ADICIONALES ---
class CampoAdicionalForm(forms.ModelForm):
    
    # --- ¡¡CAMBIO!! Hacemos 'orden' opcional y oculto ---
    # El 'required=False' es la clave para que formset.is_valid() funcione.
    orden = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CamposAdicionales
        fields = ['titulo', 'es_obligatoria', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Nombre del solicitante'
            }),
            'es_obligatoria': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            # 'orden' ya está definido arriba como HiddenInput
        }
        labels = {
            'titulo': 'Etiqueta del Campo',
            'es_obligatoria': '¿Es obligatorio?',
        }

class TipoIncidenciaForm(forms.Form):
    """
    Formulario manual para gestionar los Tipos de Incidencia.
    """
    nombre = forms.CharField(
        label="Nombre del Tipo de Incidencia",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fuga de agua'
            }
        )
    )
    descripcion = forms.CharField(
        label="Descripción Breve",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departamento = forms.ModelChoiceField(
        label="Departamento Responsable",
        queryset=Departamento.objects.filter(esta_activo=True).all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# --- EL "CONJUNTO DE FORMULARIOS" (FORMSET) ---
CamposAdicionalesFormSet = inlineformset_factory(
    Encuesta,
    CamposAdicionales,
    form=CampoAdicionalForm,
    extra=1,
    can_delete=True,
    can_order=False, # Le decimos a Django que no se preocupe por el orden
)