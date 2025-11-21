from django import forms
from django.contrib.auth.models import User

from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta
from .models import Incidencia, Vecino, EncuestaRespuesta


class IncidenciaForm(forms.Form):
    """
    Formulario manual para gestionar las Incidencias.

    Acepta parámetro 'user' en __init__ para:
    - Adaptar los campos según el rol (Territorial, SECPLA, etc.).
    - Filtrar y configurar los querysets de forma dinámica.
    """

    # ---------- Campos ----------
    encuesta = forms.ModelChoiceField(
        label="Encuesta Asociada",
        queryset=Encuesta.objects.none(),  # se setea en __init__
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    vecino = forms.ModelChoiceField(
        label="Vecino que reporta (Opcional)",
        queryset=Vecino.objects.all(),     # aunque no haya vecinos, no rompe
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
        queryset=Cuadrilla.objects.none(),  # se setea en __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    descripcion = forms.CharField(
        label="Descripción Detallada",
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3
            }
        )
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
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------- Inicialización dinámica ----------

    def __init__(self, *args, user=None, **kwargs):
        """
        Inicializa el formulario adaptando querysets y visibilidad
        de campos según el usuario conectado.
        """
        super().__init__(*args, **kwargs)

        # 1) Querysets base (para cualquier usuario)
        #    -> Todas las encuestas disponibles
        self.fields['encuesta'].queryset = Encuesta.objects.all().order_by('titulo')

        #    -> Cuadrillas activas
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)

        #    -> Vecinos (si no hay, simplemente aparece vacío; es opcional)
        self.fields['vecino'].queryset = Vecino.objects.all().order_by('id')
        self.fields['vecino'].required = False

        # Si no tenemos usuario, no seguimos adaptando por rol
        if user is None:
            return

        # 2) Intentar obtener el grupo del usuario
        try:
            group_name = user.profile.group.name
        except Exception:
            group_name = None

        # 3) Configuración específica para TERRITORIAL
        if group_name == "Territorial":
            """
            Para el Territorial:
            - Puede elegir encuesta.
            - Describe la incidencia.
            - NO asigna cuadrilla, estado ni territorial explícitamente.
            - Vecino aún no está implementado -> lo ocultamos por ahora.
            """

            # Si en el futuro quieres filtrar encuestas por algo (ej: comuna, sector, etc.),
            # este es el lugar para hacerlo. Por ahora, ve todas:
            # self.fields['encuesta'].queryset = Encuesta.objects.filter(algún_filtro_relacionado_a_user)

            # Ocultar campos que el Territorial no debe manipular
            self.fields['cuadrilla'].widget = forms.HiddenInput()
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['territorial'].widget = forms.HiddenInput()

            # Vecino todavía no está implementado -> lo dejamos oculto y opcional
            self.fields['vecino'].widget = forms.HiddenInput()
            self.fields['vecino'].required = False

            # Y nos aseguramos de que estos campos no sean requeridos
            self.fields['cuadrilla'].required = False
            self.fields['estado'].required = False
            self.fields['territorial'].required = False

        else:
            """
            Para otros roles (SECPLA, Departamento, etc.) mantenemos
            todos los campos visibles y usamos los querysets base.
            """
            self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)
            self.fields['territorial'].queryset = User.objects.filter(groups__name='Territorial')

class EncuestaRespuestaForm(forms.Form):
    valor = forms.CharField(
        label="Respuesta",
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3
            }
        )
    )
    incidencia = None
    pregunta = None

    def __init__(self, *args, incidencia=None, pregunta=None, valor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.incidencia=incidencia
        self.pregunta=pregunta
        self.fields['valor'].required = self.pregunta.es_obligatoria
        self.fields['valor'].initial = valor

