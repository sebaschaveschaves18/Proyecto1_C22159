from django.contrib import admin
from .models import Seguimiento


# Registro en Django Admin con columnas, búsqueda y filtros
@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'operador', 'tipo', 'fecha')
    list_filter = ('tipo',)
    search_fields = ('comentario', 'reporte__titulo', 'operador__username')
