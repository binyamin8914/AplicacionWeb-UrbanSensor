from rest_framework import serializers
from .models import Cuadrilla

class CuadrillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuadrilla
        fields = ['id', 'nombre', 'esta_activa']