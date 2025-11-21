# incidencias/serializers.py
from rest_framework import serializers
from .models import Incidencia

class IncidenciaSerializer(serializers.ModelSerializer):
    # Aquí le decimos: "Ve al campo 'tipo', entra y tráeme su 'nombre'"
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True, default="Sin Tipo")
    
    # "Ve al campo 'direccion', entra y tráeme su 'nombre'"
    direccion_nombre = serializers.CharField(source='direccion.nombre', read_only=True, default="Sin Dirección")
    
    # "Ve al campo 'departamento', entra y tráeme su 'nombre'"
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True, default="Sin Depto")

    class Meta:
        model = Incidencia
        # Asegúrate de incluir los campos nuevos _nombre en la lista
        fields = ['id', 'tipo_nombre', 'direccion_nombre', 'departamento_nombre', 'estado']