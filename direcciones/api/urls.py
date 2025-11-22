from django.urls import path, include
from rest_framework import routers
from .views import DireccionViewSet

router = routers.DefaultRouter()
router.register(r'', DireccionViewSet, basename='direcciones')

urlpatterns = [
    path('', include(router.urls)),
]