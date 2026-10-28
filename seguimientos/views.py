from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Seguimiento
from .permissions import SeguimientoPermisos
from .serializers import SeguimientoSerializer


# Paginación de 5 registros por página (?page=)
class SeguimientoPaginacion(PageNumberPagination):
    page_size = 5


# Listar seguimientos (GET) y registrar seguimiento (POST)
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, SeguimientoPermisos])
def seguimientos_api(request):
    if request.method == 'GET':
        seguimientos = Seguimiento.objects.select_related('reporte', 'operador').order_by('-fecha', '-id')

        # Filtros combinables: ?reporte= y ?tipo=
        reporte = request.query_params.get('reporte')
        if reporte:
            try:
                reporte_id = int(reporte)
            except ValueError:
                return Response(
                    {'reporte': 'El filtro reporte debe ser un identificador numérico.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seguimientos = seguimientos.filter(reporte_id=reporte_id)

        tipo = request.query_params.get('tipo')
        if tipo:
            seguimientos = seguimientos.filter(tipo=tipo.strip().upper())

        paginador = SeguimientoPaginacion()
        pagina = paginador.paginate_queryset(seguimientos, request)
        serializer = SeguimientoSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    # Registrar seguimiento: el operador es siempre el usuario del token
    data = request.data.copy()
    data['operador'] = request.user.id
    serializer = SeguimientoSerializer(data=data)
    if serializer.is_valid():
        seguimiento = serializer.save()

        # Decisión automática: el primer seguimiento pasa el reporte de RECIBIDO a EN_PROCESO
        reporte = seguimiento.reporte
        if reporte.estado == 'RECIBIDO':
            reporte.estado = 'EN_PROCESO'
            reporte.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalle (GET), actualizar (PUT/PATCH) y eliminar (DELETE) un seguimiento
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, SeguimientoPermisos])
def seguimiento_detalle_api(request, pk):
    try:
        seguimiento = Seguimiento.objects.select_related('reporte').get(pk=pk)
    except Seguimiento.DoesNotExist:
        return Response(
            {'error': 'Seguimiento no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = SeguimientoSerializer(seguimiento)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = SeguimientoSerializer(
            seguimiento,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # Solo admin (SeguimientoPermisos)
        seguimiento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
