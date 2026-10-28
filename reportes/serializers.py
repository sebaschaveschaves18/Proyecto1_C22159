from django.utils import timezone
from rest_framework import serializers
from .models import Reporte, ESTADOS_CERRADOS, TRANSICIONES


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = '__all__'
        # Campos que llena el sistema, el cliente no los puede enviar
        read_only_fields = ['prioridad', 'fecha_creacion', 'fecha_resolucion']

    # RN-03: el título no puede quedar vacío
    def validate_titulo(self, value):
        titulo_limpio = value.strip()
        if not titulo_limpio:
            raise serializers.ValidationError('El título es obligatorio.')
        return titulo_limpio

    # RN-03: la descripción debe explicar el problema (mínimo 10 caracteres)
    def validate_descripcion(self, value):
        descripcion_limpia = value.strip()
        if len(descripcion_limpia) < 10:
            raise serializers.ValidationError(
                'La descripción debe tener al menos 10 caracteres.'
            )
        return descripcion_limpia

    def validate_distrito(self, value):
        distrito_limpio = value.strip()
        if not distrito_limpio:
            raise serializers.ValidationError('El distrito es obligatorio.')
        return distrito_limpio

    def validate_direccion(self, value):
        direccion_limpia = value.strip()
        if not direccion_limpia:
            raise serializers.ValidationError('La dirección es obligatoria.')
        return direccion_limpia

    # RN-04: no se puede usar una categoría inactiva
    def validate_categoria(self, value):
        # En una actualización se permite conservar la categoría que ya tenía
        if self.instance and self.instance.categoria_id == value.id:
            return value
        if not value.activo:
            raise serializers.ValidationError(
                'No se puede reportar en una categoría inactiva.'
            )
        return value

    def validate(self, data):
        categoria = data.get('categoria')
        ciudadano = data.get('ciudadano')
        distrito = data.get('distrito')
        estado = data.get('estado')

        if self.instance:
            # RN-06: un reporte cerrado (RESUELTO o RECHAZADO) ya no se modifica
            if self.instance.estado in ESTADOS_CERRADOS:
                raise serializers.ValidationError({
                    'estado': 'El reporte está cerrado y no se puede modificar.'
                })

            # El ciudadano que creó el reporte no se puede cambiar
            if ciudadano is not None and ciudadano != self.instance.ciudadano:
                raise serializers.ValidationError({
                    'ciudadano': 'No se puede cambiar el ciudadano del reporte.'
                })

            # En PATCH se usan los valores actuales cuando un campo no viene en la solicitud
            if categoria is None:
                categoria = self.instance.categoria
            if ciudadano is None:
                ciudadano = self.instance.ciudadano
            if distrito is None:
                distrito = self.instance.distrito
            if estado is None:
                estado = self.instance.estado

            # RN-06: solo se permiten los cambios de estado definidos en TRANSICIONES
            if estado != self.instance.estado and estado not in TRANSICIONES[self.instance.estado]:
                raise serializers.ValidationError({
                    'estado': f'No se puede pasar de {self.instance.estado} a {estado}.'
                })

            # RN-07: al resolver se guarda automáticamente la fecha de resolución
            if estado == 'RESUELTO':
                data['fecha_resolucion'] = timezone.now()
        else:
            # Un reporte nuevo siempre inicia en RECIBIDO
            if estado is not None and estado != 'RECIBIDO':
                raise serializers.ValidationError({
                    'estado': 'Un reporte nuevo debe iniciar en estado RECIBIDO.'
                })
            estado = 'RECIBIDO'

            # RN-07: la prioridad se copia de la categoría (decisión automática)
            if categoria:
                data['prioridad'] = categoria.prioridad_base

        # RN-05: el ciudadano no puede tener dos reportes abiertos
        # de la misma categoría en el mismo distrito
        if estado not in ESTADOS_CERRADOS and categoria and ciudadano and distrito:
            duplicados = Reporte.objects.filter(
                ciudadano=ciudadano,
                categoria=categoria,
                distrito__iexact=distrito,
            ).exclude(estado__in=ESTADOS_CERRADOS)
            # Al actualizar no se compara el reporte consigo mismo
            if self.instance:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                raise serializers.ValidationError({
                    'categoria': 'Ya tiene un reporte abierto de esta categoría en este distrito.'
                })

        return data
