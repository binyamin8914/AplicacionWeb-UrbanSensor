from django.urls import path
from . import views

urlpatterns = [
    # Perfil encargado 
    path('mi-departamento/dashboard/',                     views.departamento_dashboard,     name='departamentos_dashboard'),
    path('mi-departamento/incidencias/',                   views.incidencias_por_estado,     name='departamentos_incidencias'),
    path('mi-departamento/incidencias/<int:incidencia_id>/', views.incidencia_ver_y_derivar, name='departamentos_incidencia_detalle'),
    path('mi-departamento/incidencias/estado/<str:estado>/', views.incidencias_por_estado,   name='departamentos_incidencias_estado'),

    # --- Aliases de compatibilidad (nombres viejos) ---
    path('',                                   views.departamento_listar,     name='departamento_listar'),
    path('actualizar/',                        views.departamento_actualizar, name='departamento_crear'),
    path('actualizar/<int:departamento_id>/',  views.departamento_actualizar, name='departamento_actualizar'),
    path('ver/<int:departamento_id>/',         views.departamento_ver,        name='departamento_ver'),
    path('bloquear/<int:departamento_id>/',    views.departamento_bloquear,   name='departamento_bloquear'),
]
