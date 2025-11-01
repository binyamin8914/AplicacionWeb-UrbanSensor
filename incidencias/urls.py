from django.urls import path
from . import views

urlpatterns = [
    # CRUD Tipos de incidencia
    path('tipos/', views.listar_tipos_incidencia, name='listar_tipos_incidencia'),
    path('tipos/crear/', views.crear_tipo_incidencia, name='crear_tipo_incidencia'),
    path('tipos/editar/<int:tipo_id>/', views.editar_tipo_incidencia, name='editar_tipo_incidencia'),
    path('tipos/eliminar/<int:tipo_id>/', views.eliminar_tipo_incidencia, name='eliminar_tipo_incidencia'),

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

    # NUEVAS URLs PARA EL DASHBOARD Y LISTADO SECPLA
    path('secpla/dashboard/', views.secpla_dashboard, name='secpla_dashboard'),
    path('secpla/listado/', views.secpla_incidencias_list, name='secpla_listado_todas'),
    path('secpla/listado/<str:status>/', views.secpla_incidencias_list, name='secpla_listado_filtrado'),
    # Detalle de incidencia (solo visualización)
    path('detalle/<int:incidencia_id>/', views.detalle_incidencia, name='incidencia_detalle'),

]