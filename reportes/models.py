from django.contrib.auth.models import User
from django.db import models
from categorias.models import Categoria

# Estados en los que el reporte ya terminó y no se puede modificar
ESTADOS_CERRADOS = ['RESUELTO', 'RECHAZADO']

# Cambios de estado permitidos: estado actual -> estados siguientes válidos
TRANSICIONES = {
    'RECIBIDO': ['EN_PROCESO', 'RECHAZADO'],
    'EN_PROCESO': ['RESUELTO', 'RECHAZADO'],
    'RESUELTO': [],
    'RECHAZADO': [],
}


class Reporte(models.Model):
    # Reporte que crea un ciudadano sobre un problema de su comunidad
    ESTADOS = [
        ('RECIBIDO', 'Recibido'),
        ('EN_PROCESO', 'En proceso'),
        ('RESUELTO', 'Resuelto'),
        ('RECHAZADO', 'Rechazado'),
    ]
    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500)
    # Relación 1:N -> una categoría tiene muchos reportes. PROTECT: no se borra con reportes.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='reportes',
    )
    # Relación 1:N -> un usuario (ciudadano) crea muchos reportes. Usa el usuario nativo de Django.
    ciudadano = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reportes',
    )
    distrito = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200)          # Otras señas del lugar
    estado = models.CharField(max_length=20, choices=ESTADOS, default='RECIBIDO')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    fecha_creacion = models.DateTimeField(auto_now_add=True)      # Se llena sola al crear
    fecha_resolucion = models.DateTimeField(null=True, blank=True)  # Se llena al pasar a RESUELTO

    def __str__(self):
        return f'#{self.id} {self.titulo} - {self.estado}'
