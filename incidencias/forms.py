from django import forms
from django.contrib.auth.models import User

from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta
from .models import Incidencia, Vecino, EncuestaRespuesta
from registration.models import Profile  # <-- AGREGAR ESTE IMPORT

class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = [
            "encuesta",
            "prioridad",
            "descripcion",
            "latitud",
            "longitud",
            "direccion_textual",
            "vecino",
            "territorial",
            "cuadrilla",
            "estado",
        ]
        widgets = {
            "encuesta": forms.Select(attrs={"class": "form-select"}),
            "prioridad": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "latitud": forms.NumberInput(attrs={"class": "form-control"}),
            "longitud": forms.NumberInput(attrs={"class": "form-control"}),
            "direccion_textual": forms.TextInput(attrs={"class": "form-control"}),
            "vecino": forms.Select(attrs={"class": "form-select"}),
            "territorial": forms.Select(attrs={"class": "form-select"}),
            "cuadrilla": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Force choices (evita problemas por import/carga o sobrescrituras)
        self.fields['prioridad'].choices = list(Incidencia.PRIORIDAD_CHOICES)
        # default initial
        if not self.fields['prioridad'].initial:
            self.fields['prioridad'].initial = 'normal'

        # Querysets base
        self.fields['encuesta'].queryset = Encuesta.objects.all().order_by('titulo')
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)
        self.fields['vecino'].queryset = Vecino.objects.all().order_by('id')
        self.fields['vecino'].required = False

        if user is None:
            return

        # Determinar rol de forma robusta
        try:
            is_territorial = user.groups.filter(name__iexact='territorial').exists()
        except Exception:
            is_territorial = False

        if is_territorial:
            # Si el territorial tiene direccion, filtrar encuestas vigentes
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = None

            if profile and getattr(profile, 'direccion', None):
                self.fields['encuesta'].queryset = Encuesta.objects.filter(
                    tipo_incidencia__departamento__direccion=profile.direccion,
                    estado='vigente'
                ).order_by('-id')
            else:
                self.fields['encuesta'].queryset = Encuesta.objects.none()

            # Ocultar campos que el Territorial no debe manipular
            self.fields['cuadrilla'].widget = forms.HiddenInput()
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['territorial'].widget = forms.HiddenInput()
            self.fields['vecino'].widget = forms.HiddenInput()

            # <-- LÍNEAS AÑADIR: marcar como no requeridos si los ocultamos -->
            self.fields['cuadrilla'].required = False
            self.fields['estado'].required = False
            self.fields['territorial'].required = False
            self.fields['vecino'].required = False
            # <-- fin de líneas añadidas -->

            # Asegurar widget y requerido para prioridad
            self.fields['prioridad'].widget = forms.Select(attrs={'class': 'form-select'})
            self.fields['prioridad'].required = True

        else:
            # Para otros roles ocultar prioridad
            self.fields['prioridad'].widget = forms.HiddenInput()
            self.fields['prioridad'].required = False

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

