from django.contrib import admin
from .models import TipoIncidencia, Incidencia, Evidencia

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento')
    search_fields = ('nombre',)

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'encuesta', 'direccion', 'departamento', 'estado', 'created_at')
    list_filter = ('estado', 'departamento')

admin.site.register(Evidencia)
