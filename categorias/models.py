from django.db import models
from instituciones.models import Institucion


class Categoria(models.Model):
    # Tipo de problema que se puede reportar (ej: Sin luz, Daño en carretera, Sin agua)
    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    # Relación 1:N -> una institución atiende muchas categorías.
    # PROTECT: no se puede borrar una institución que tenga categorías.
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='categorias',
    )
    # Prioridad que se copia automáticamente a cada reporte nuevo
    prioridad_base = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    activo = models.BooleanField(default=True)   # Inactiva = no recibe reportes nuevos

    def __str__(self):
        return self.nombre
