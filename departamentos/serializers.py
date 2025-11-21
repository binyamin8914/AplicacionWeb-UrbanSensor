# departamentos/serializers.py
from rest_framework import serializers
from .models import Departamento

class DepartamentoSerializer(serializers.ModelSerializer):
    # Agregamos campos extra para mostrar nombres en lugar de solo IDs
    encargado_nombre = serializers.CharField(source='encargado.get_full_name', read_only=True)
    direccion_nombre = serializers.CharField(source='direccion.nombre', read_only=True)

    class Meta:
        model = Departamento
        # Incluimos todos los campos que usa tu tabla de Angular
        fields = ['id', 'nombre', 'encargado_nombre', 'direccion_nombre', 'esta_activo']