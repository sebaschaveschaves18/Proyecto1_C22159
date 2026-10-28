from django.db import models


class Institucion(models.Model):
    # Entidad pública que atiende los reportes (ej: AyA, CNFL, MOPT, Municipalidad)
    nombre = models.CharField(max_length=100, unique=True)   # Único: no se repiten instituciones
    siglas = models.CharField(max_length=15, unique=True)    # Único: ej. AYA, CNFL
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)                    # Opcional, pero debe ser un correo válido
    activo = models.BooleanField(default=True)               # Inactiva = no recibe nuevas categorías

    class Meta:
        verbose_name_plural = 'Instituciones'

    def __str__(self):
        return f'{self.siglas} - {self.nombre}'
