"""
URL configuration for UrbanSensor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from core.urls import core_urlpatterns
from rest_framework.routers import DefaultRouter
from departamentos.views import DepartamentoViewSet
from incidencias.views import IncidenciaViewSet
from incidencias.views import DashboardStatsView

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'incidencias', IncidenciaViewSet)

urlpatterns = [
    path('', include(core_urlpatterns)),
    path('admin/', admin.site.urls),

    # Apps del proyecto (SIN namespaces)
    path('administracion/', include('administracion.urls')),
    path('direcciones/', include('direcciones.urls')),
    path('departamentos/', include('departamentos.urls')),
    path('cuadrillas/', include('cuadrillas.urls')),

    # Otras apps
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('registration.urls')),
    path('encuestas/', include('encuestas.urls')),
    path('incidencias/', include('incidencias.urls')),
    #angular
    path('api/', include(router.urls)),
    path('api/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats')
]
