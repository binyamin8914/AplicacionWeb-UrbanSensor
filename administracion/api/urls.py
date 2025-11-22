from rest_framework import routers
from .views import UsersViewSet, GroupViewSet, current_profile
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'usuarios', UsersViewSet, basename='usuarios')
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/me/', current_profile),
]