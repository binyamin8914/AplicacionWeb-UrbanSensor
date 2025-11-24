from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.cuadrilla_listar,     name='cuadrilla_listar'),
    path('actualizar/',                    views.cuadrilla_actualizar, name='cuadrilla_crear'),
    path('actualizar/<int:cuadrilla_id>/', views.cuadrilla_actualizar, name='cuadrilla_actualizar'),
    path('ver/<int:cuadrilla_id>/',        views.cuadrilla_ver,        name='cuadrilla_ver'),
    path('bloquear/<int:cuadrilla_id>/',   views.cuadrilla_bloquear,   name='cuadrilla_bloquear'),
    # rutas api
    path('api/list',                      views.api_cuadrilla_list),
    path('api/bloquear',                  views.api_cuadrilla_bloquear),
    path('api/public/list/',                      views.api_cuadrilla_list_public),
    path('api/<int:cuadrilla_id>/', views.api_cuadrilla_detail),
    path('api/create/',                     views.api_cuadrilla_create),
    path('api/form-data/', views.api_form_data)
    
]
