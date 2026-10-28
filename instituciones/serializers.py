from rest_framework import serializers
from .models import Institucion


class InstitucionSerializer(serializers.ModelSerializer):
    # Se quitan los validadores automáticos de unique para dar mensajes propios
    nombre = serializers.CharField(max_length=100, validators=[])
    siglas = serializers.CharField(max_length=15, validators=[])

    class Meta:
        model = Institucion
        fields = '__all__'

    # RN-01: nombre obligatorio y sin duplicados (sin importar mayúsculas)
    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if not nombre_limpio:
            raise serializers.ValidationError('El nombre es obligatorio.')

        instituciones = Institucion.objects.filter(nombre__iexact=nombre_limpio)
        # Al actualizar se excluye el propio registro
        if self.instance:
            instituciones = instituciones.exclude(pk=self.instance.pk)
        if instituciones.exists():
            raise serializers.ValidationError('Ya existe una institución con ese nombre.')
        return nombre_limpio

    # RN-01: siglas obligatorias, en mayúscula y sin duplicados
    def validate_siglas(self, value):
        siglas_limpias = value.strip().upper()
        if not siglas_limpias:
            raise serializers.ValidationError('Las siglas son obligatorias.')

        instituciones = Institucion.objects.filter(siglas__iexact=siglas_limpias)
        if self.instance:
            instituciones = instituciones.exclude(pk=self.instance.pk)
        if instituciones.exists():
            raise serializers.ValidationError('Ya existe una institución con esas siglas.')
        return siglas_limpias

    # El teléfono no puede quedar vacío
    def validate_telefono(self, value):
        telefono_limpio = value.strip()
        if not telefono_limpio:
            raise serializers.ValidationError('El teléfono es obligatorio.')
        return telefono_limpio
