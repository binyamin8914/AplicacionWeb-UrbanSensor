from django import forms
from django.contrib.auth.models import User
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla
from direcciones.models import Direccion   # 👈 IMPORTANTE
from encuestas.models import Encuesta, Vecino
from .models import Incidencia, TipoIncidencia

class TipoIncidenciaForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre del Tipo de Incidencia",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Fuga de agua'})
    )
    descripcion = forms.CharField(
        label="Descripción Breve",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departamento = forms.ModelChoiceField(
        label="Departamento Responsable",
        queryset=Departamento.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class IncidenciaForm(forms.Form):
    encuesta = forms.ModelChoiceField(
        label="Encuesta Asociada",
        queryset=Encuesta.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vecino = forms.ModelChoiceField(
        label="Vecino que reporta (Opcional)",
        queryset=Vecino.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    territorial = forms.ModelChoiceField(
        label="Agente Territorial",
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cuadrilla = forms.ModelChoiceField(
        label="Cuadrilla Asignada",
        queryset=Cuadrilla.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # 👇 NUEVOS
    direccion = forms.ModelChoiceField(
        label="Dirección incidencia",
        queryset=Direccion.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    departamento = forms.ModelChoiceField(
        label="Departamento incidencia",
        queryset=Departamento.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    descripcion = forms.CharField(
        label="Descripción Detallada",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    latitud = forms.DecimalField(
        label="Latitud (Opcional)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    longitud = forms.DecimalField(
        label="Longitud (Opcional)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    direccion_textual = forms.CharField(
        label="Dirección Escrita (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        label="Estado Actual",
        choices=Incidencia.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # se cargan en tiempo real:
        self.fields['encuesta'].queryset = Encuesta.objects.all().order_by('titulo')
        self.fields['vecino'].queryset = Vecino.objects.all().order_by('nombre')
        self.fields['territorial'].queryset = User.objects.filter(groups__name='TERRITORIAL').order_by('username')
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.all().order_by('nombre')
        self.fields['direccion'].queryset = Direccion.objects.all().order_by('id')
        self.fields['departamento'].queryset = Departamento.objects.all().order_by('nombre')
