from django.contrib import admin
from .models import Departamento

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "correo_encargado", "esta_activo", "direccion", "get_encargado")
    list_filter = ("esta_activo", "direccion")
    search_fields = ("nombre", "correo_encargado")
    ordering = ("nombre",)

    def get_encargado(self, obj):
        # si tu modelo tiene FK/Char 'encargado'; si no, muestra guion
        return getattr(obj, "encargado", "—")
    get_encargado.short_description = "Encargado"
