from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.direccion_listar,     name='direccion_listar'),
    path('actualizar/',                    views.direccion_actualizar, name='direccion_crear'),
    path('actualizar/<int:direccion_id>/', views.direccion_actualizar, name='direccion_actualizar'),
    path('ver/<int:direccion_id>/',        views.direccion_ver,        name='direccion_ver'),
    path('bloquear/<int:direccion_id>/',   views.direccion_bloquear,   name='direccion_bloquear'),
]
