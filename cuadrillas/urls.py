from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.cuadrilla_listar,     name='cuadrilla_listar'),
    path('actualizar/',                    views.cuadrilla_actualizar, name='cuadrilla_crear'),
    path('actualizar/<int:cuadrilla_id>/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),
    path('ver/<int:cuadrilla_id>/',        views.cuadrilla_ver,        name='cuadrilla_ver'),
    path('bloquear/<int:cuadrilla_id>/',   views.cuadrilla_bloquear,   name='cuadrilla_bloquear'),
]
