from rest_framework import serializers
from direcciones.models import Direccion


class DireccionSerializer(serializers.ModelSerializer):
    encargado_nombre = serializers.CharField(source='encargado.get_full_name', read_only=True)
    
    class Meta:
        model = Direccion
        fields = ['id', 'nombre', 'encargado', 'encargado_nombre', 'esta_activa']
        read_only_fields = ['encargado_nombre']