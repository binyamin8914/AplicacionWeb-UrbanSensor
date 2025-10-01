from django.urls import path
from heroes import views

heroes_urlpatterns = [
    path('main_habilidad/', views.main_habilidad, name='main_habilidad'),
    path('habilidad_crear/', views.habilidad_crear, name='habilidad_crear'),
    path('habilidad_guardar/', views.habilidad_guardar, name='habilidad_guardar'),
    path('habilidad_ver/<habilidad_id>/',views.habilidad_ver,name='habilidad_ver'),
    path('habilidad_actualiza/', views.habilidad_actualiza, name='habilidad_actualiza'),
    path('habilidad_actualiza/<habilidad_id>/', views.habilidad_actualiza, name='habilidad_actualiza'),
    path('habilidad_bloquea/<habilidad_id>/', views.habilidad_bloquea, name='habilidad_bloquea'),
    path('habilidad_elimina/<habilidad_id>/', views.habilidad_elimina, name='habilidad_elimina'),
]
