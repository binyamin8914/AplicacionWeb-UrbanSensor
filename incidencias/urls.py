from django.urls import path
from . import views

urlpatterns = [
    
    path('gestion/', views.gestion_incidencias, name='gestion_incidencias'),

 
    path('crear/', views.crear_incidencia, name='crear_incidencia'),
    path('editar/<int:incidencia_id>/', views.editar_incidencia, name='editar_incidencia'),
    path('eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='eliminar_incidencia'),
    path('confirmar-eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='confirmar_eliminar_incidencia'),

    
    path('derivar/<int:incidencia_id>/', views.derivar_incidencia, name='derivar_incidencia'),
    path('finalizar/<int:incidencia_id>/', views.finalizar_incidencia, name='finalizar_incidencia'),
    path("incidencia/<int:incidencia_id>/rechazar/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("incidencia/<int:incidencia_id>/aceptar/", views.aceptar_incidencia, name="aceptar_incidencia"),

   
    path('detalle/<int:incidencia_id>/', views.detalle_incidencia, name='incidencia_detalle'),
    path('api/campos_encuesta/<int:encuesta_id>/', views.api_campos_encuesta, name='api_campos_encuesta'),
]
