from rest_framework import serializers
from .models import Incidencia

class IncidenciaSerializer(serializers.ModelSerializer):
    # 1. EL TIPO: Entramos a 'encuesta', luego a 'tipo_incidencia', luego sacamos el 'nombre'
    # (Nota: Si tu modelo en Encuesta se llama distinto a 'tipo_incidencia', avísame)
    tipo_nombre = serializers.CharField(
        source='encuesta.tipo_incidencia.nombre', 
        read_only=True, 
        default="Sin Tipo"
    )
    
    # 2. EL DEPARTAMENTO: El departamento suele estar ligado al Tipo de Incidencia
    departamento_nombre = serializers.CharField(
        source='encuesta.tipo_incidencia.departamento.nombre', 
        read_only=True, 
        default="Sin Depto"
    )

    # 3. LA DIRECCIÓN: 
    # Opción A: Usamos la dirección textual que guardaste en la incidencia
    direccion_nombre = serializers.CharField(
        source='direccion_textual', 
        read_only=True, 
        default="Sin Dirección"
    )
    # Opción B (Alternativa): Si la dirección está en la encuesta, sería:
    # source='encuesta.direccion.nombre'

    class Meta:
        model = Incidencia
        fields = ['id', 'tipo_nombre', 'direccion_nombre', 'departamento_nombre', 'estado']