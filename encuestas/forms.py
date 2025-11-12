from django import forms
from .models import Encuesta, CamposAdicionales
from departamentos.models import Departamento
from incidencias.models import TipoIncidencia
from django.forms import inlineformset_factory

print("¡¡CARGANDO FORMS.PY DE ENCUESTAS!! (Versión 4, 'orden' no obligatorio)")

# --- FORMULARIO PRINCIPAL DE LA ENCUESTA ---
class EncuestaForm(forms.ModelForm):
    
    tipo_incidencia = forms.ModelChoiceField(
        queryset=TipoIncidencia.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Seleccione un tipo de incidencia",
        label="Tipo de incidencia"
    )
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Seleccione un departamento"
    )
    class Meta:
        model = Encuesta
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        activos = Departamento.objects.filter(esta_activo=True).order_by('nombre')
        self.fields['departamento'].queryset = activos if activos.exists() else Departamento.objects.all().order_by('nombre')


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


# --- EL "CONJUNTO DE FORMULARIOS" (FORMSET) ---
CamposAdicionalesFormSet = inlineformset_factory(
    Encuesta,
    CamposAdicionales,
    form=CampoAdicionalForm,
    extra=1,
    can_delete=True,
    can_order=False, # Le decimos a Django que no se preocupe por el orden
)