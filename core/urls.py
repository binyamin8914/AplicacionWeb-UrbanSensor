from django.urls import path
from core import views


core_urlpatterns = [
    path('', views.home, name='home'),
    path('check_profile', views.check_profile, name='check_profile'),
    path('dashboard', views.dashboard, name='dashboard'),

   
    path(
        'territorial/incidencias/nueva/',
        views.territorial_crear_incidencia,
        name='territorial_crear_incidencia'
    ),
]
