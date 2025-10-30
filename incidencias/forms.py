from django import forms
from django.contrib.auth.models import User
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla
from encuestas.models import Encuesta, Vecino
from .models import Incidencia, TipoIncidencia

class TipoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = TipoIncidencia
        fields = ['nombre', 'descripcion', 'departamento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }

class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion_textual': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['encuesta'].queryset = Encuesta.objects.all().order_by('titulo')
        self.fields['vecino'].queryset = Vecino.objects.all().order_by('nombre')
        self.fields['territorial'].queryset = User.objects.filter(groups__name='TERRITORIAL').order_by('username')
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.all().order_by('nombre')
