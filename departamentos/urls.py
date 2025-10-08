from django.urls import path
from . import views

urlpatterns = [
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
    path('departamentos/actualizar/', views.departamento_actualizar, name='departamento_actualizar'),  # Crear
    path('departamentos/actualizar/<departamento_id>/', views.departamento_actualizar, name='departamento_actualizar'),  # Editar
    path('departamentos/ver/<departamento_id>/', views.departamento_ver, name='departamento_ver'),
    path('departamentos/bloquear/<departamento_id>/', views.departamento_bloquear, name='departamento_bloquear'),
]