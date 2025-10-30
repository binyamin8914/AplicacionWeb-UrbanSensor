from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/', views.usuarios_listar, name='usuarios_listar'),
    path('usuarios/actualizar/', views.usuario_actualizar, name='usuario_actualizar'),  # Crear
    path('usuarios/actualizar/<user_id>/', views.usuario_actualizar, name='usuario_actualizar'),  # Editar
    path('usuarios/ver/<user_id>/', views.usuario_ver, name='usuario_ver'),
    path('usuarios/bloquear/<user_id>/', views.usuario_bloquear, name='usuario_bloquear'),
]