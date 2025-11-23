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
    path('secpla/dashboard/', views.secpla_dashboard, name='secpla_dashboard'),
    path('secpla/listado/', views.secpla_incidencias_list, name='secpla_listado_todas'),
    path('secpla/listado/<str:status>/', views.secpla_incidencias_list, name='secpla_listado_filtrado'),
    path('detalle/<int:incidencia_id>/', views.detalle_incidencia, name='incidencia_detalle'),

]