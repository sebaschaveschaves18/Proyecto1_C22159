from django.contrib.auth.models import User
from django.db import models
from reportes.models import Reporte


class Apoyo(models.Model):
    # Un ciudadano indica "a mí también me afecta" en el reporte de otra persona.
    # Es la tabla intermedia de la relación N:M entre usuarios y reportes.
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,   # Si se elimina el reporte, se eliminan sus apoyos
        related_name='apoyos',
    )
    ciudadano = models.ForeignKey(
        User,
        on_delete=models.CASCADE,   # Si se elimina el usuario, se eliminan sus apoyos
        related_name='apoyos',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        # RN-10: un ciudadano solo puede apoyar una vez el mismo reporte
        constraints = [
            models.UniqueConstraint(
                fields=['reporte', 'ciudadano'],
                name='apoyo_unico_reporte_ciudadano'
            )
        ]

    def __str__(self):
        return f'{self.ciudadano} apoya reporte #{self.reporte_id}'
