from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Institucion
from .permissions import InstitucionPermisos
from .serializers import InstitucionSerializer


# Paginación de 5 registros por página (?page=)
class InstitucionPaginacion(PageNumberPagination):
    page_size = 5


# Listar instituciones (GET) y crear institución (POST)
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([InstitucionPermisos])
def instituciones_api(request):
    if request.method == 'GET':
        instituciones = Institucion.objects.all()

        # Filtro ?activo=true/false
        activo = request.query_params.get('activo')
        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            instituciones = instituciones.filter(activo=activo.lower() == 'true')

        # Ordenamiento ?ordering=nombre o -nombre
        orden = request.query_params.get('ordering', 'id')
        if orden == 'nombre':
            instituciones = instituciones.order_by('nombre', 'id')
        elif orden == '-nombre':
            instituciones = instituciones.order_by('-nombre', 'id')
        else:
            instituciones = instituciones.order_by('id')

        # Se pagina el resultado y se devuelve con count/next/previous/results
        paginador = InstitucionPaginacion()
        pagina = paginador.paginate_queryset(instituciones, request)
        serializer = InstitucionSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    # Crear institución: el serializer valida los datos
    serializer = InstitucionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalle (GET), actualizar (PUT/PATCH) y eliminar (DELETE) una institución
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([InstitucionPermisos])
def institucion_detalle_api(request, pk):
    # Si el id no existe se responde 404
    try:
        institucion = Institucion.objects.get(pk=pk)
    except Institucion.DoesNotExist:
        return Response(
            {'error': 'Institución no encontrada.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = InstitucionSerializer(institucion)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        # PATCH permite enviar solo algunos campos (partial=True)
        serializer = InstitucionSerializer(
            institucion,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # RN-11: no se elimina si tiene categorías asociadas (on_delete=PROTECT) -> 409
        try:
            institucion.delete()
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar la institución porque tiene categorías asociadas.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
