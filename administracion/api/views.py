from rest_framework import viewsets, permissions, decorators, response
from django.contrib.auth import get_user_model
from registration.models import Profile
from .serializers import UserSerializer, ProfileSerializer, GroupSerializer
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes as perm_decorator
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


# VIEWSET principal de usuarios
class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('profile', 'profile__group', 'profile__direccion').all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberPagination

    # Filtro por perfil
    def get_queryset(self):
        qs = super().get_queryset()
        perfil = self.request.query_params.get('perfil')
        if perfil:
            qs = qs.filter(profile__group__name=perfil)
        return qs

    # toggle activar/bloquear
    @decorators.action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return response.Response({"status": "ok", "is_active": user.is_active})


# LISTADO DE GRUPOS PARA REACT
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Sin paginación para grupos


# PERFIL DEL USUARIO LOGEADO
@api_view(['GET'])
@perm_decorator([permissions.AllowAny])  # Temporalmente para desarrollo
def current_profile(request):
    # Para desarrollo, devolver perfil simulado si no está autenticado
    if not request.user.is_authenticated:
        return Response({"group": "SECPLA"})
    
    try:
        profile = Profile.objects.select_related('group', 'direccion').get(user=request.user)
        return Response(ProfileSerializer(profile).data)
    except Profile.DoesNotExist:
        # Si no tiene perfil, devolver SECPLA por defecto para desarrollo
        return Response({"group": "SECPLA"})