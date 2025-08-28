from django.urls import path
from heroes import views

heroes_urlpatterns = [
    path('main_habilidad', views.main_habilidad, name='main_habilidad'),
]
