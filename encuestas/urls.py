from django.urls import path
from . import views

urlpatterns = [
    path('tipos/', views.listar_tipos_incidencia, name='listar_tipos_incidencia'),
    path('tipos/crear/', views.crear_tipo_incidencia, name='crear_tipo_incidencia'),
    path('tipos/editar/<int:tipo_id>/', views.editar_tipo_incidencia, name='editar_tipo_incidencia'),
    path('tipos/eliminar/<int:tipo_id>/', views.eliminar_tipo_incidencia, name='eliminar_tipo_incidencia'),

    path('', views.gestion_encuestas, name='gestion_encuestas'),
    path('crear/', views.crear_encuesta, name='crear_encuesta'),
    path('<int:encuesta_id>/editar/', views.editar_encuesta, name='editar_encuesta'),
    path('<int:encuesta_id>/eliminar/', views.eliminar_encuesta, name='eliminar_encuesta'),
    path('<int:encuesta_id>/cambiar-estado/', views.cambiar_estado_encuesta, name='cambiar_estado_encuesta'),
]