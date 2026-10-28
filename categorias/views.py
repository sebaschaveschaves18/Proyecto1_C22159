from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Categoria
from .permissions import CategoriaPermisos
from .serializers import CategoriaSerializer


# Paginación de 5 registros por página (?page=)
class CategoriaPaginacion(PageNumberPagination):
    page_size = 5


# Listar categorías (GET) y crear categoría (POST)
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([CategoriaPermisos])
def categorias_api(request):
    if request.method == 'GET':
        # select_related trae la institución en la misma consulta (evita consultas extra)
        categorias = Categoria.objects.select_related('institucion').order_by('nombre')

        # Filtros combinables: ?institucion=, ?prioridad=, ?activo=
        institucion = request.query_params.get('institucion')
        if institucion:
            try:
                institucion_id = int(institucion)
            except ValueError:
                return Response(
                    {'institucion': 'El filtro institucion debe ser un identificador numérico.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            categorias = categorias.filter(institucion_id=institucion_id)

        prioridad = request.query_params.get('prioridad')
        if prioridad:
            categorias = categorias.filter(prioridad_base=prioridad.strip().upper())

        activo = request.query_params.get('activo')
        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            categorias = categorias.filter(activo=activo.lower() == 'true')

        paginador = CategoriaPaginacion()
        pagina = paginador.paginate_queryset(categorias, request)
        serializer = CategoriaSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    # Crear categoría: el serializer valida nombre e institución
    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalle (GET), actualizar (PUT/PATCH) y eliminar (DELETE) una categoría
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([CategoriaPermisos])
def categoria_detalle_api(request, pk):
    try:
        categoria = Categoria.objects.select_related('institucion').get(pk=pk)
    except Categoria.DoesNotExist:
        return Response(
            {'error': 'Categoría no encontrada.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = CategoriaSerializer(categoria)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = CategoriaSerializer(
            categoria,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # RN-11: no se elimina si tiene reportes asociados (on_delete=PROTECT) -> 409
        try:
            categoria.delete()
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar la categoría porque tiene reportes asociados.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
