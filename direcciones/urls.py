from django.urls import path
from . import views

urlpatterns = [
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/actualizar/', views.direccion_actualizar, name='direccion_actualizar'),  # Crear
    path('direcciones/actualizar/<direccion_id>/', views.direccion_actualizar, name='direccion_actualizar'),  # Editar
    path('direcciones/ver/<direccion_id>/', views.direccion_ver, name='direccion_ver'),
    path('direcciones/bloquear/<direccion_id>/', views.direccion_bloquear, name='direccion_bloquear'),
]