from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Apoyo
from .permissions import ApoyoPermisos
from .serializers import ApoyoSerializer

# Cantidad de apoyos con la que un reporte sube a prioridad ALTA
APOYOS_PARA_PRIORIDAD_ALTA = 3


# Listar apoyos (GET) y apoyar un reporte (POST)
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ApoyoPermisos])
def apoyos_api(request):
    if request.method == 'GET':
        apoyos = Apoyo.objects.select_related('reporte', 'ciudadano').order_by('-fecha', '-id')

        # Filtro ?reporte= para ver quién apoya un reporte
        reporte = request.query_params.get('reporte')
        if reporte:
            try:
                reporte_id = int(reporte)
            except ValueError:
                return Response(
                    {'reporte': 'El filtro reporte debe ser un identificador numérico.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            apoyos = apoyos.filter(reporte_id=reporte_id)

        serializer = ApoyoSerializer(apoyos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Apoyar: el ciudadano es siempre el usuario del token
    data = request.data.copy()
    data['ciudadano'] = request.user.id
    serializer = ApoyoSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    reporte = serializer.validated_data['reporte']

    # RN-10: si ya apoyó este reporte se responde 409 (conflicto con un registro existente)
    if Apoyo.objects.filter(reporte=reporte, ciudadano=request.user).exists():
        return Response(
            {'error': 'Ya apoyó este reporte.'},
            status=status.HTTP_409_CONFLICT,
        )

    serializer.save()

    # Decisión automática: con 3 o más apoyos el reporte sube a prioridad ALTA
    if reporte.apoyos.count() >= APOYOS_PARA_PRIORIDAD_ALTA and reporte.prioridad != 'ALTA':
        reporte.prioridad = 'ALTA'
        reporte.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Detalle (GET) y eliminar (DELETE) un apoyo.
# No hay PUT/PATCH: un apoyo no tiene datos que editar (se elimina y se vuelve a crear).
@api_view(['GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ApoyoPermisos])
def apoyo_detalle_api(request, pk):
    try:
        apoyo = Apoyo.objects.get(pk=pk)
    except Apoyo.DoesNotExist:
        return Response(
            {'error': 'Apoyo no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(ApoyoSerializer(apoyo).data)

    # Eliminar: solo el ciudadano que dio el apoyo o un administrador
    if apoyo.ciudadano != request.user and not request.user.is_staff:
        return Response(
            {'detail': 'Solo puede eliminar sus propios apoyos.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    apoyo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
