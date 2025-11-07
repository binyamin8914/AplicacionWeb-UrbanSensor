from django.urls import path
from . import views

urlpatterns = [
    path('cuadrillas/', views.cuadrilla_listar, name='cuadrilla_listar'),
    path('cuadrillas/actualizar/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),  # Crear
    path('cuadrillas/actualizar/<cuadrilla_id>/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),  # Editar
    path('cuadrillas/ver/<cuadrilla_id>/', views.cuadrilla_ver, name='cuadrilla_ver'),
    path('cuadrillas/bloquear/<cuadrilla_id>/', views.cuadrilla_bloquear, name='cuadrilla_bloquear'),
]