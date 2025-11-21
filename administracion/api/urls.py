from rest_framework import routers
from .views import UsersViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'usuarios', UsersViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls)),
]