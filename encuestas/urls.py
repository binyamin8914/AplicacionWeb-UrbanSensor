from django.urls import path
from . import views

urlpatterns = [
    path('gestion/', views.gestion_encuestas, name='gestion_encuestas'),
    path('crear/', views.crear_encuesta, name='crear_encuesta'),
    path('editar/<int:encuesta_id>/', views.editar_encuesta, name='editar_encuesta'),
    path('eliminar/<int:encuesta_id>/', views.eliminar_encuesta, name='eliminar_encuesta'),
]