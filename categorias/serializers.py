from rest_framework import serializers
from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    # Se quita el validador automático de unique para dar un mensaje propio
    nombre = serializers.CharField(max_length=60, validators=[])

    class Meta:
        model = Categoria
        fields = '__all__'

    # RN-02: nombre obligatorio y sin duplicados (sin importar mayúsculas)
    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if not nombre_limpio:
            raise serializers.ValidationError('El nombre es obligatorio.')

        categorias = Categoria.objects.filter(nombre__iexact=nombre_limpio)
        # Al actualizar se excluye el propio registro
        if self.instance:
            categorias = categorias.exclude(pk=self.instance.pk)
        if categorias.exists():
            raise serializers.ValidationError('Ya existe una categoría con ese nombre.')
        return nombre_limpio

    # RN-02: no se puede asignar una institución inactiva
    def validate_institucion(self, value):
        if not value.activo:
            raise serializers.ValidationError(
                'No se puede asignar una institución inactiva.'
            )
        return value
