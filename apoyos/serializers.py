from rest_framework import serializers
from reportes.models import ESTADOS_CERRADOS
from .models import Apoyo


class ApoyoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apoyo
        fields = '__all__'
        read_only_fields = ['fecha']
        # Se quita el validador automático del UniqueConstraint:
        # el duplicado se revisa en la vista para responder 409 (conflicto)
        validators = []

    def validate(self, data):
        reporte = data.get('reporte')
        ciudadano = data.get('ciudadano')

        # RN-09: no se puede apoyar un reporte cerrado
        if reporte.estado in ESTADOS_CERRADOS:
            raise serializers.ValidationError({
                'reporte': 'No se puede apoyar un reporte cerrado.'
            })

        # RN-09: el ciudadano no puede apoyar su propio reporte
        if reporte.ciudadano == ciudadano:
            raise serializers.ValidationError({
                'reporte': 'No puede apoyar su propio reporte.'
            })

        return data
