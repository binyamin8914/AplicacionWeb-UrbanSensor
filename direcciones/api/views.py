from rest_framework import viewsets, permissions
from direcciones.models import Direccion
from .serializers import DireccionSerializer


class DireccionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Direccion.objects.filter(esta_activa=True).order_by('nombre')
    serializer_class = DireccionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Sin paginación para direcciones