from django.contrib import admin
from .models import Reporte


# Registro en Django Admin con columnas, búsqueda y filtros
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'categoria', 'ciudadano', 'distrito', 'estado', 'prioridad', 'fecha_creacion')
    list_filter = ('estado', 'prioridad', 'categoria')
    search_fields = ('titulo', 'descripcion', 'distrito', 'ciudadano__username')
