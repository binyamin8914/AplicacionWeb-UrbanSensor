from django.contrib import admin
from .models import Incidencia, TipoIncidencia

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    # uso métodos para no depender de nombres exactos en el modelo
    list_display = ("id", "descripcion", "get_estado", "get_prioridad", "get_departamento", "get_tipo")
    list_select_related = ("tipo_incidencia",)  # optimiza queries
    list_filter = ("estado",)                   # agrega 'prioridad' o 'departamento' si existen en tu modelo
    search_fields = ("descripcion",)
    ordering = ("-id",)

    def get_estado(self, obj):
        return getattr(obj, "get_estado_display", lambda: getattr(obj, "estado", "—"))()
    get_estado.short_description = "Estado"

    def get_prioridad(self, obj):
        return getattr(obj, "prioridad", "—")
    get_prioridad.short_description = "Prioridad"

    def get_departamento(self, obj):
        # 1) FK directa en Incidencia
        if hasattr(obj, "departamento") and getattr(obj, "departamento"):
            return getattr(obj.departamento, "nombre", obj.departamento)
        # 2) A través del tipo de incidencia
        if hasattr(obj, "tipo_incidencia") and obj.tipo_incidencia and hasattr(obj.tipo_incidencia, "departamento"):
            dep = obj.tipo_incidencia.departamento
            return getattr(dep, "nombre", dep) if dep else "—"
        return "—"
    get_departamento.short_description = "Departamento"

    def get_tipo(self, obj):
        return getattr(getattr(obj, "tipo_incidencia", None), "nombre", "—")
    get_tipo.short_description = "Tipo incidencia"

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "departamento")
    list_filter = ("departamento",)
    search_fields = ("nombre",)
    ordering = ("nombre",)
