from django.urls import path
from . import views

urlpatterns = [
    # URLs para Incidencias
    path('gestion/', views.gestion_incidencias, name='gestion_incidencias'),
    path('crear/', views.crear_incidencia, name='crear_incidencia'),
    path('editar/<int:incidencia_id>/', views.editar_incidencia, name='editar_incidencia'),
    path('eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='eliminar_incidencia'),

    # URLs para Tipos de Incidencia
    path('tipos/', views.listar_tipos_incidencia, name='listar_tipos_incidencia'),
    path('tipos/crear/', views.crear_tipo_incidencia, name='crear_tipo_incidencia'),
    path('tipos/editar/<int:tipo_id>/', views.editar_tipo_incidencia, name='editar_tipo_incidencia'),
    path('tipos/eliminar/<int:tipo_id>/', views.eliminar_tipo_incidencia, name='eliminar_tipo_incidencia'),
]