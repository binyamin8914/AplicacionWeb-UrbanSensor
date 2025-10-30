from django.contrib import admin
from .models import Encuesta, CamposAdicionales, EncuestaRespuesta

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "get_estado", "get_prioridad", "departamento", "tipo_incidencia")
    list_filter = ("estado", "prioridad", "departamento")
    search_fields = ("titulo",)
    ordering = ("-id",)
    autocomplete_fields = ("departamento", "tipo_incidencia")

    def get_estado(self, obj):
        return obj.get_estado_display() if hasattr(obj, "get_estado_display") else getattr(obj, "estado", "—")
    get_estado.short_description = "Estado"

    def get_prioridad(self, obj):
        return obj.get_prioridad_display() if hasattr(obj, "get_prioridad_display") else getattr(obj, "prioridad", "—")
    get_prioridad.short_description = "Prioridad"

admin.site.register(CamposAdicionales)
admin.site.register(EncuestaRespuesta)
