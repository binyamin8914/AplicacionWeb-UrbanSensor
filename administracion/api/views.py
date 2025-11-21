from rest_framework import viewsets, permissions
from .serializers import SimpleUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.AllowAny]  # Cambia luego por permisos reales