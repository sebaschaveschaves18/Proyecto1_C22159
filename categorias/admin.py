from django.contrib import admin
from .models import Categoria


# Registro en Django Admin con columnas, búsqueda y filtros
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'institucion', 'prioridad_base', 'activo')
    search_fields = ('nombre', 'institucion__nombre')
    list_filter = ('prioridad_base', 'activo', 'institucion')
