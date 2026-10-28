from django.contrib import admin
from .models import Institucion


# Registro en Django Admin con columnas, búsqueda y filtros
@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ('siglas', 'nombre', 'telefono', 'email', 'activo')
    search_fields = ('nombre', 'siglas')
    list_filter = ('activo',)
