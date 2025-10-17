# encuestas/forms.py
from django import forms
from .models import Encuesta
from departamentos.models import Departamento

class EncuestaForm(forms.ModelForm):
    # 🔒 Forzamos el queryset a nivel de clase (fallback)
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),   # se sobreescribe en __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione un departamento"
    )

    class Meta:
        model = Encuesta
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_incidencia': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            # 'departamento' ya se definió arriba
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Filtra por activos y ordena; si no hay activos, mostrará todos
        activos = Departamento.objects.filter(esta_activo=True).order_by('nombre')
        self.fields['departamento'].queryset = activos if activos.exists() else Departamento.objects.all().order_by('nombre')
