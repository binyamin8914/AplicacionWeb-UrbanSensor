from rest_framework import serializers
from .models import Incidencia

class IncidenciaSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(
        source='encuesta.tipo_incidencia.nombre', 
        read_only=True, 
        default="Sin Tipo"
    )
    departamento_nombre = serializers.CharField(
        source='encuesta.tipo_incidencia.departamento.nombre', 
        read_only=True, 
        default="Sin Depto"
    )
    direccion_nombre = serializers.CharField(
        source='direccion_textual', 
        read_only=True, 
        default="Sin Dirección"
    )
    class Meta:
        model = Incidencia
        fields = ['id', 'tipo_nombre', 'direccion_nombre', 'departamento_nombre', 'estado']