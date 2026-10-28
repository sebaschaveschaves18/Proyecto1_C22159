from rest_framework import serializers
from reportes.models import ESTADOS_CERRADOS
from .models import Seguimiento


class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'
        read_only_fields = ['fecha']

    # RN-08: el comentario es obligatorio (mínimo 5 caracteres)
    def validate_comentario(self, value):
        comentario_limpio = value.strip()
        if len(comentario_limpio) < 5:
            raise serializers.ValidationError(
                'El comentario debe tener al menos 5 caracteres.'
            )
        return comentario_limpio

    def validate(self, data):
        reporte = data.get('reporte')
        operador = data.get('operador')

        if self.instance:
            # No se puede mover el seguimiento a otro reporte ni cambiar el operador
            if reporte is not None and reporte != self.instance.reporte:
                raise serializers.ValidationError({
                    'reporte': 'No se puede cambiar el reporte del seguimiento.'
                })
            if operador is not None and operador != self.instance.operador:
                raise serializers.ValidationError({
                    'operador': 'No se puede cambiar el operador del seguimiento.'
                })
            # En PATCH se usa el reporte actual
            reporte = self.instance.reporte

        # RN-08: no se registran ni editan seguimientos de un reporte cerrado
        if reporte and reporte.estado in ESTADOS_CERRADOS:
            raise serializers.ValidationError({
                'reporte': 'El reporte está cerrado; no admite seguimientos.'
            })

        return data
