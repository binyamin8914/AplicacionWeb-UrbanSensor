from django import forms
from django.contrib.auth.models import User
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta, Vecino
from .models import Incidencia, TipoIncidencia

class TipoIncidenciaForm(forms.Form):
    """
    Formulario manual para gestionar los Tipos de Incidencia.
    """
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
    """
    Formulario manual para gestionar las Incidencias.
    """
    encuesta = forms.ModelChoiceField(
        label="Encuesta Asociada",
        queryset=Encuesta.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vecino = forms.ModelChoiceField(
        label="Vecino que reporta (Opcional)",
        queryset=Vecino.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    territorial = forms.ModelChoiceField(
        label="Agente Territorial",
        queryset=User.objects.filter(groups__name='TERRITORIAL'), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cuadrilla = forms.ModelChoiceField(
        label="Cuadrilla Asignada",
        queryset=Cuadrilla.objects.all(), 
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