from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    # --- Usuarios ---
    path('usuarios/', views.usuarios_listar, name='usuarios_listar'),
    path('usuarios/actualizar/', views.usuario_actualizar, name='usuario_actualizar'),  # Crear
    path('usuarios/actualizar/<user_id>/', views.usuario_actualizar, name='usuario_actualizar'),  # Editar
    path('usuarios/ver/<user_id>/', views.usuario_ver, name='usuario_ver'),
    path('usuarios/bloquear/<user_id>/', views.usuario_bloquear, name='usuario_bloquear'),

    # --- Direcciones ---
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/actualizar/', views.direccion_actualizar, name='direccion_actualizar'),  # Crear
    path('direcciones/actualizar/<direccion_id>/', views.direccion_actualizar, name='direccion_actualizar'),  # Editar
    path('direcciones/ver/<direccion_id>/', views.direccion_ver, name='direccion_ver'),
    path('direcciones/bloquear/<direccion_id>/', views.direccion_bloquear, name='direccion_bloquear'),

    # --- Departamentos ---
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
    path('departamentos/actualizar/', views.departamento_actualizar, name='departamento_actualizar'),  # Crear
    path('departamentos/actualizar/<departamento_id>/', views.departamento_actualizar, name='departamento_actualizar'),  # Editar
    path('departamentos/ver/<departamento_id>/', views.departamento_ver, name='departamento_ver'),
    path('departamentos/bloquear/<departamento_id>/', views.departamento_bloquear, name='departamento_bloquear'),

    # --- Cuadrillas ---
    path('cuadrillas/', views.cuadrilla_listar, name='cuadrilla_listar'),
    path('cuadrillas/actualizar/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),  # Crear
    path('cuadrillas/actualizar/<cuadrilla_id>/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),  # Editar
    path('cuadrillas/ver/<cuadrilla_id>/', views.cuadrilla_ver, name='cuadrilla_ver'),
    path('cuadrillas/bloquear/<cuadrilla_id>/', views.cuadrilla_bloquear, name='cuadrilla_bloquear'),
]