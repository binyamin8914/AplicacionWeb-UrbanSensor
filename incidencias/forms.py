from django import forms
from django.contrib.auth.models import User

from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta
from .models import Incidencia, Vecino
from registration.models import Profile  

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

        
        self.fields['prioridad'].choices = list(Incidencia.PRIORIDAD_CHOICES)
        
        if not self.fields['prioridad'].initial:
            self.fields['prioridad'].initial = 'normal'

        
        self.fields['encuesta'].queryset = Encuesta.objects.all().order_by('-id')
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)
        self.fields['vecino'].queryset = Vecino.objects.all().order_by('id')
        self.fields['vecino'].required = False

        if user is None:
            return

        
        try:
            is_territorial = user.groups.filter(name__iexact='territorial').exists()
        except Exception:
            is_territorial = False

        if is_territorial:
            
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

            
            self.fields['cuadrilla'].widget = forms.HiddenInput()
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['territorial'].widget = forms.HiddenInput()
            self.fields['vecino'].widget = forms.HiddenInput()

            
            self.fields['cuadrilla'].required = False
            self.fields['estado'].required = False
            self.fields['territorial'].required = False
            self.fields['vecino'].required = False
           

            
            self.fields['prioridad'].widget = forms.Select(attrs={'class': 'form-select'})
            self.fields['prioridad'].required = True

        else:
            
            self.fields['prioridad'].widget = forms.HiddenInput()
            self.fields['prioridad'].required = False

            self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(esta_activa=True)
            self.fields['territorial'].queryset = User.objects.filter(groups__name='Territorial')
