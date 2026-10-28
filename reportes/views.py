from django.db.models import Count, Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from categorias.models import Categoria
from instituciones.models import Institucion
from seguimientos.serializers import SeguimientoSerializer
from .models import Reporte
from .permissions import ReportePermisos
from .serializers import ReporteSerializer


# Paginación de 5 registros por página (?page=)
class ReportePaginacion(PageNumberPagination):
    page_size = 5


# Ordenamientos permitidos en ?ordering=
ORDENAMIENTOS = ['fecha_creacion', '-fecha_creacion', 'titulo', '-titulo']


# Listar reportes (GET) y crear reporte (POST)
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ReportePermisos])
def reportes_api(request):
    if request.method == 'GET':
        # select_related trae categoría, institución y ciudadano en una sola consulta
        reportes = Reporte.objects.select_related(
            'categoria', 'categoria__institucion', 'ciudadano'
        ).all()

        # Filtros combinables: ?estado=, ?prioridad=, ?distrito=, ?categoria=, ?institucion=
        estado = request.query_params.get('estado')
        if estado:
            reportes = reportes.filter(estado=estado.strip().upper())

        prioridad = request.query_params.get('prioridad')
        if prioridad:
            reportes = reportes.filter(prioridad=prioridad.strip().upper())

        distrito = request.query_params.get('distrito')
        if distrito:
            reportes = reportes.filter(distrito__iexact=distrito.strip())

        categoria = request.query_params.get('categoria')
        if categoria:
            try:
                categoria_id = int(categoria)
            except ValueError:
                return Response(
                    {'categoria': 'El filtro categoria debe ser un identificador numérico.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            reportes = reportes.filter(categoria_id=categoria_id)

        # Filtro por relación: reportes de las categorías que atiende una institución
        institucion = request.query_params.get('institucion')
        if institucion:
            try:
                institucion_id = int(institucion)
            except ValueError:
                return Response(
                    {'institucion': 'El filtro institucion debe ser un identificador numérico.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            reportes = reportes.filter(categoria__institucion_id=institucion_id)

        # Búsqueda ?buscar= en título, descripción o dirección (Q permite usar OR)
        buscar = request.query_params.get('buscar')
        if buscar:
            reportes = reportes.filter(
                Q(titulo__icontains=buscar)
                | Q(descripcion__icontains=buscar)
                | Q(direccion__icontains=buscar)
            )

        # Ordenamiento ?ordering= (por defecto los más recientes primero)
        orden = request.query_params.get('ordering', '-fecha_creacion')
        if orden not in ORDENAMIENTOS:
            orden = '-fecha_creacion'
        reportes = reportes.order_by(orden, '-id')

        paginador = ReportePaginacion()
        pagina = paginador.paginate_queryset(reportes, request)
        serializer = ReporteSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    # Crear reporte: el ciudadano es siempre el usuario del token
    data = request.data.copy()
    data['ciudadano'] = request.user.id
    serializer = ReporteSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalle (GET), actualizar (PUT/PATCH) y eliminar (DELETE) un reporte
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ReportePermisos])
def reporte_detalle_api(request, pk):
    try:
        reporte = Reporte.objects.select_related('categoria', 'ciudadano').get(pk=pk)
    except Reporte.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = ReporteSerializer(reporte)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        # El serializer valida estado, transiciones y duplicados también en PATCH
        serializer = ReporteSerializer(
            reporte,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # Solo admin (ReportePermisos). Sus seguimientos y apoyos se borran en cascada.
        reporte.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Reportes del usuario autenticado (filtro por la relación ciudadano)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_reportes_api(request):
    reportes = Reporte.objects.select_related('categoria').filter(
        ciudadano=request.user
    ).order_by('-fecha_creacion', '-id')

    paginador = ReportePaginacion()
    pagina = paginador.paginate_queryset(reportes, request)
    serializer = ReporteSerializer(pagina, many=True)
    return paginador.get_paginated_response(serializer.data)


# Historial de un reporte: el reporte, sus seguimientos y la cantidad de apoyos
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def historial_reporte_api(request, pk):
    try:
        # prefetch_related carga los seguimientos (relación inversa) en una consulta aparte
        reporte = Reporte.objects.prefetch_related('seguimientos__operador').annotate(
            total_apoyos=Count('apoyos')
        ).get(pk=pk)
    except Reporte.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    seguimientos = reporte.seguimientos.all()
    return Response({
        'reporte': ReporteSerializer(reporte).data,
        'total_apoyos': reporte.total_apoyos,
        'seguimientos': SeguimientoSerializer(seguimientos, many=True).data,
    })


# Estadísticas generales: solo administradores
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def estadisticas_api(request):
    # Cantidad de reportes agrupados por estado (agregación con values + annotate)
    por_estado = list(
        Reporte.objects.values('estado').annotate(total=Count('id')).order_by('estado')
    )

    # Cantidad de reportes por categoría (relación inversa categoria.reportes)
    por_categoria = list(
        Categoria.objects.annotate(total_reportes=Count('reportes'))
        .values('id', 'nombre', 'total_reportes')
        .order_by('-total_reportes', 'nombre')
    )

    # Institución con más reportes abiertos (Count con filtro Q a través de dos relaciones)
    mayor = Institucion.objects.annotate(
        reportes_abiertos=Count(
            'categorias__reportes',
            filter=Q(categorias__reportes__estado__in=['RECIBIDO', 'EN_PROCESO'])
        )
    ).order_by('-reportes_abiertos', 'nombre').first()

    institucion_mayor = None
    if mayor:
        institucion_mayor = {
            'id': mayor.id,
            'siglas': mayor.siglas,
            'reportes_abiertos': mayor.reportes_abiertos,
        }

    # Los 5 reportes con más apoyos ciudadanos
    mas_apoyados = list(
        Reporte.objects.annotate(total_apoyos=Count('apoyos'))
        .filter(total_apoyos__gt=0)
        .order_by('-total_apoyos', 'id')
        .values('id', 'titulo', 'estado', 'total_apoyos')[:5]
    )

    return Response({
        'total_reportes': Reporte.objects.count(),
        'reportes_abiertos': Reporte.objects.filter(
            estado__in=['RECIBIDO', 'EN_PROCESO']
        ).count(),
        'por_estado': por_estado,
        'por_categoria': por_categoria,
        'institucion_mas_reportes_abiertos': institucion_mayor,
        'reportes_mas_apoyados': mas_apoyados,
    })


# Perfil del usuario autenticado y su rol
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil_api(request):
    grupos = list(request.user.groups.values_list('name', flat=True))

    # El rol se decide por is_staff o por el grupo al que pertenece
    if request.user.is_staff:
        rol = 'Administrador'
    elif 'Operadores' in grupos:
        rol = 'Operador'
    elif 'Ciudadanos' in grupos:
        rol = 'Ciudadano'
    else:
        rol = 'Sin rol'

    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'rol': rol,
        'grupos': grupos,
    })
