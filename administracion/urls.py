
from django.urls import path
from . import views

urlpatterns = [
    
    path('usuarios/',                          views.usuarios_listar,     name='usuarios_listar'),
    path('usuarios/nuevo/',                    views.usuario_actualizar,  name='usuario_actualizar'),
    path('usuarios/editar/<int:user_id>/',     views.usuario_actualizar,  name='usuario_actualizar_id'),
    path('usuarios/bloquear/<int:user_id>/',   views.usuario_bloquear,    name='usuario_bloquear'),
    path('usuarios/ver/<int:user_id>/',        views.usuario_ver,         name='usuario_ver'),
]
