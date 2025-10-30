from django.contrib import admin
from .models import Direccion

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    """
    Admin seguro: usa métodos get_... para no depender de nombres exactos.
    Muestra nombre, encargado, correo y estado.
    """
    list_display = ("id", "get_nombre", "get_encargado", "get_correo", "get_activo")
    list_filter = ()
    search_fields = ("nombre",)
    ordering = ("nombre",)

    def get_nombre(self, obj):
        return getattr(obj, "nombre", "—")
    get_nombre.short_description = "Nombre"

    def get_encargado(self, obj):
        # intenta buscar cualquier campo posible relacionado al encargado
        for field in ["nombre_encargado", "encargado", "encargado_nombre"]:
            if hasattr(obj, field):
                return getattr(obj, field)
        return "—"
    get_encargado.short_description = "Encargado"

    def get_correo(self, obj):
        for field in ["correo_encargado", "email_encargado", "correo"]:
            if hasattr(obj, field):
                return getattr(obj, field)
        return "—"
    get_correo.short_description = "Correo"

    def get_activo(self, obj):
        for field in ["esta_activo", "activo", "is_active"]:
            if hasattr(obj, field):
                return "✅" if getattr(obj, field) else "❌"
        return "—"
    get_activo.short_description = "Activo"
