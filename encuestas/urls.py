from django.urls import path
from . import views

urlpatterns = [
    path('', views.gestion_encuestas, name='gestion_encuestas'),
    path('crear/', views.crear_encuesta, name='crear_encuesta'),
    path('<int:encuesta_id>/editar/', views.editar_encuesta, name='editar_encuesta'),
    path('<int:encuesta_id>/eliminar/', views.eliminar_encuesta, name='eliminar_encuesta'),
]
