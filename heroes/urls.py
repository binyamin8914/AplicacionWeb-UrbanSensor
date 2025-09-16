from django.urls import path
from heroes import views

heroes_urlpatterns = [
    path('main_habilidad/', views.main_habilidad, name='main_habilidad'),
    path('habilidad_crear/', views.habilidad_crear, name='habilidad_crear'),
    path('habilidad_guardar/', views.habilidad_guardar, name='habilidad_guardar'),
]
