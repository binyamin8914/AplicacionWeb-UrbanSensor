from django.urls import path
from . import views

urlpatterns = [
    # Gestión de incidencias (listado unificado según rol)
    path('gestion/', views.gestion_incidencias, name='gestion_incidencias'),

    # Crear / editar / eliminar incidencia
    path('crear/', views.crear_incidencia, name='crear_incidencia'),
    path('editar/<int:incidencia_id>/', views.editar_incidencia, name='editar_incidencia'),
    path('eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='eliminar_incidencia'),
    path('confirmar-eliminar/<int:incidencia_id>/', views.eliminar_incidencia, name='confirmar_eliminar_incidencia'),

    # Derivar / finalizar
    path('derivar/<int:incidencia_id>/', views.derivar_incidencia, name='derivar_incidencia'),
    path('finalizar/<int:incidencia_id>/', views.finalizar_incidencia, name='finalizar_incidencia'),

    # Detalle de incidencia (solo visualización)
    path('detalle/<int:incidencia_id>/', views.detalle_incidencia, name='incidencia_detalle'),

]