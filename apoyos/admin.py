from django.contrib import admin
from .models import Apoyo


# Registro en Django Admin con columnas y búsqueda
@admin.register(Apoyo)
class ApoyoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'ciudadano', 'fecha')
    search_fields = ('reporte__titulo', 'ciudadano__username')
