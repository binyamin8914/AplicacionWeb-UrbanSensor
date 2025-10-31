from django.urls import path
from . import views

urlpatterns = [
    # rutas para CRUD
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
    path('departamentos/actualizar/', views.departamento_actualizar, name='departamento_actualizar'),
    path('departamentos/actualizar/<departamento_id>/', views.departamento_actualizar, name='departamento_actualizar'),
    path('departamentos/ver/<departamento_id>/', views.departamento_ver, name='departamento_ver'),
    path('departamentos/bloquear/<departamento_id>/', views.departamento_bloquear, name='departamento_bloquear'),

    # Rutas para el perfil Departamento (encargado)
    path('mi-departamento/dashboard/', views.departamento_dashboard, name='departamento_dashboard'),
    path('mi-departamento/incidencias/', views.incidencias_por_estado, name='incidencias_por_estado'),
    path('mi-departamento/incidencias/<int:incidencia_id>/', views.incidencia_ver_y_derivar, name='incidencia_ver_y_derivar'),
    path('mi-departamento/incidencias/<str:estado>/', views.incidencias_por_estado, name='incidencias_por_estado'),
]