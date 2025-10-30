from django.urls import path
from . import views

app_name = 'incidencias'

urlpatterns = [
    path('gestion/', views.gestion_incidencias, name='gestion_incidencias'),
    path('crear/', views.crear_incidencia, name='crear_incidencia'),
    path('editar/<int:incidencia_id>/', views.editar_incidencia, name='editar_incidencia'),
    path('eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='eliminar_incidencia'),
]
