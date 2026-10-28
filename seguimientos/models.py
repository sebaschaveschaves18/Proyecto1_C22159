from django.contrib.auth.models import User
from django.db import models
from reportes.models import Reporte


class Seguimiento(models.Model):
    # Avance que registra un operador sobre un reporte (inspección, reparación, comentario)
    TIPOS = [
        ('COMENTARIO', 'Comentario'),
        ('INSPECCION', 'Inspección'),
        ('REPARACION', 'Reparación'),
    ]

    # Relación 1:N -> un reporte tiene muchos seguimientos.
    # CASCADE: si se elimina el reporte, se eliminan sus seguimientos.
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='seguimientos',
    )
    # Operador (usuario de Django) que registró el avance
    operador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='seguimientos',
    )
    tipo = models.CharField(max_length=20, choices=TIPOS, default='COMENTARIO')
    comentario = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)   # Se llena sola al crear

    def __str__(self):
        return f'Reporte #{self.reporte_id} - {self.tipo}'
