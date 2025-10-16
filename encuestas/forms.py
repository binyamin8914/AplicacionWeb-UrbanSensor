from django import forms
from .models import Encuesta

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        
        # Incluye todos los campos de tu modelo en el formulario
        fields = '__all__' 
        
        # O si prefieres, especifica solo los campos que quieres mostrar:
        # fields = ['titulo', 'descripcion', 'tipo_incidencia', 'estado', 'prioridad', 'departamento']

        # (Opcional) Puedes añadir widgets para personalizar cómo se ven los campos
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_incidencia': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }