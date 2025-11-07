from django import forms
from django.contrib.auth.models import User
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta, Vecino
from .models import Incidencia

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
    Acepta parámetro 'user' en __init__ para filtrar choices y adaptar la UI.
    """
    encuesta = forms.ModelChoiceField(
        label="Encuesta Asociada",
        queryset=Encuesta.objects.none(), 
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
        queryset=User.objects.filter(groups__name='Territorial'), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cuadrilla = forms.ModelChoiceField(
        label="Cuadrilla Asignada",
        queryset=Cuadrilla.objects.none(), 
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
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, user=None, **kwargs):
        """
        Inicializa el formulario adaptando querysets y campos según el usuario.
        - Si user pertenece al grupo 'Territorial' filtramos encuestas (ej. vigentes)
          y ocultamos/inactivamos campos que no debe ver (cuadrilla, estado, territorial).
        - Para otros roles mostramos valores por defecto.
        """
        super().__init__(*args, **kwargs)

        # Por defecto mostrar todas las encuestas y cuadrillas activas
        self.fields['encuesta'].queryset = Encuesta.objects.filter(estado='vigente')
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)

        if user is None:
            return

        # Obtener nombre del grupo si existe profile
        group_name = None
        try:
            group_name = user.profile.group.name
        except Exception:
            group_name = None

        if group_name == "Territorial":
            # Territorial sólo debe elegir encuesta (vigentes) y no asignar cuadrilla/estado/territorial
            self.fields['encuesta'].queryset = Encuesta.objects.filter(estado='vigente')
            # Ocultar campos que el territorial no debe manipular
            self.fields['cuadrilla'].widget = forms.HiddenInput()
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['territorial'].widget = forms.HiddenInput()

            # Opcional: marcar como no requeridos
            self.fields['cuadrilla'].required = False
            self.fields['estado'].required = False
            self.fields['territorial'].required = False
        else:
            # Para SECPLA u otros roles: mostrar todas las encuestas (no sólo vigentes)
            self.fields['encuesta'].queryset = Encuesta.objects.all()
            # cuadrillas activas
            self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)