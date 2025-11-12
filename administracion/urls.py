from django.urls import path
from . import views

# NO usamos namespaces (app_name)

urlpatterns = [
    # --- URLs de Usuarios (Las que ya tenías) ---
    path('usuarios/', views.usuarios_listar, name='usuarios_listar'),
    path('usuarios/nuevo/', views.usuario_actualizar, name='usuario_actualizar'), # Para crear
    path('usuarios/editar/<int:user_id>/', views.usuario_actualizar, name='usuario_actualizar_id'), # Para editar
    path('usuarios/bloquear/<int:user_id>/', views.usuario_bloquear, name='usuario_bloquear'),
    path('usuarios/ver/<int:user_id>/', views.usuario_ver, name='usuario_ver'),

    # --- URLs de Direcciones (Las que faltaban) ---
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/nuevo/', views.direccion_actualizar, name='direccion_crear'), 
    path('direcciones/editar/<int:id>/', views.direccion_actualizar, name='direccion_actualizar'), 
    path('direcciones/bloquear/<int:id>/', views.direccion_bloquear, name='direccion_bloquear'), 

    # --- URLs de Departamentos (Las que faltaban) ---
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
    path('departamentos/nuevo/', views.departamento_actualizar, name='departamento_crear'), 
    path('departamentos/editar/<int:id>/', views.departamento_actualizar, name='departamento_actualizar'), 
    path('departamentos/bloquear/<int:id>/', views.departamento_bloquear, name='departamento_bloquear'), 

    # --- URLs de Cuadrillas (Las que faltaban) ---
    path('cuadrillas/', views.cuadrilla_listar, name='cuadrilla_listar'),
    path('cuadrillas/nuevo/', views.cuadrilla_actualizar, name='cuadrilla_crear'), 
    path('cuadrillas/editar/<int:id>/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'), 
    path('cuadrillas/bloquear/<int:id>/', views.cuadrilla_bloquear, name='cuadrilla_bloquear'), 
]