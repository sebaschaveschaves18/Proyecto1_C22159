from django.contrib.auth.models import Group, Permission, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from categorias.models import Categoria
from instituciones.models import Institucion
from .models import Reporte


class ReportesAPITests(APITestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre='Compañía Nacional de Fuerza y Luz', siglas='CNFL', telefono='2295-5000'
        )
        self.categoria = Categoria.objects.create(
            nombre='Sin electricidad', institucion=self.institucion, prioridad_base='ALTA'
        )

        # Grupo Ciudadanos con add_reporte
        self.grupo_ciudadanos = Group.objects.create(name='Ciudadanos')
        self.grupo_ciudadanos.permissions.set(Permission.objects.filter(
            content_type__app_label='reportes', codename__in=['add_reporte'],
        ))
        # Grupo Operadores con change_reporte
        self.grupo_operadores = Group.objects.create(name='Operadores')
        self.grupo_operadores.permissions.set(Permission.objects.filter(
            content_type__app_label='reportes', codename__in=['change_reporte'],
        ))

        self.ciudadano = User.objects.create_user(username='ciudadano', password='ClaveSegura123!')
        self.ciudadano.groups.add(self.grupo_ciudadanos)
        self.operador = User.objects.create_user(username='operador', password='ClaveSegura123!')
        self.operador.groups.add(self.grupo_operadores)

        # Por defecto las solicitudes se hacen como ciudadano
        self.usar_token(self.ciudadano)

    def usar_token(self, usuario):
        token, _ = Token.objects.get_or_create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def datos_reporte(self, **cambios):
        datos = {
            'titulo': 'Barrio sin luz',
            'descripcion': 'Desde anoche no hay electricidad en toda la cuadra.',
            'categoria': self.categoria.pk,
            'distrito': 'Puntarenas',
            'direccion': '100 m norte de la escuela',
        }
        datos.update(cambios)
        return datos

    def crear_reporte(self, **cambios):
        datos = {
            'titulo': 'Barrio sin luz',
            'descripcion': 'Desde anoche no hay electricidad en toda la cuadra.',
            'categoria': self.categoria,
            'ciudadano': self.ciudadano,
            'distrito': 'Puntarenas',
            'direccion': '100 m norte de la escuela',
        }
        datos.update(cambios)
        return Reporte.objects.create(**datos)

    # CRUD: el ciudadano crea un reporte -> 201, con prioridad copiada de la categoría (RN-07)
    def test_ciudadano_crea_reporte(self):
        respuesta = self.client.post('/api/reportes/', self.datos_reporte(), format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['ciudadano'], self.ciudadano.pk)
        self.assertEqual(respuesta.data['prioridad'], 'ALTA')
        self.assertEqual(respuesta.data['estado'], 'RECIBIDO')

    # Permisos: listar sin token -> 401
    def test_listado_sin_token_devuelve_401(self):
        self.client.credentials()
        respuesta = self.client.get('/api/reportes/')
        self.assertEqual(respuesta.status_code, 401)

    # Permisos: un operador (no es del grupo Ciudadanos) no crea reportes -> 403
    def test_operador_no_puede_crear_reporte(self):
        self.usar_token(self.operador)
        respuesta = self.client.post('/api/reportes/', self.datos_reporte(), format='json')
        self.assertEqual(respuesta.status_code, 403)

    # Permisos: un ciudadano no puede eliminar reportes (solo admin) -> 403
    def test_ciudadano_no_puede_eliminar_reporte(self):
        reporte = self.crear_reporte()
        respuesta = self.client.delete(f'/api/reportes/{reporte.pk}/')
        self.assertEqual(respuesta.status_code, 403)

    # CRUD: el administrador elimina un reporte -> 204
    def test_admin_elimina_reporte(self):
        reporte = self.crear_reporte()
        admin = User.objects.create_superuser(
            username='admin_pruebas', email='admin@example.com', password='ClaveSegura123!'
        )
        self.usar_token(admin)
        respuesta = self.client.delete(f'/api/reportes/{reporte.pk}/')
        self.assertEqual(respuesta.status_code, 204)
        self.assertFalse(Reporte.objects.filter(pk=reporte.pk).exists())

    # RN-03: descripción muy corta -> 400
    def test_descripcion_corta_devuelve_400(self):
        respuesta = self.client.post(
            '/api/reportes/', self.datos_reporte(descripcion='Sin luz'), format='json'
        )
        self.assertEqual(respuesta.status_code, 400)

    # RN-04: categoría inactiva -> 400
    def test_categoria_inactiva_devuelve_400(self):
        self.categoria.activo = False
        self.categoria.save()
        respuesta = self.client.post('/api/reportes/', self.datos_reporte(), format='json')
        self.assertEqual(respuesta.status_code, 400)

    # RN-05: dos reportes abiertos de la misma categoría y distrito -> 400
    def test_no_permite_reporte_duplicado_abierto(self):
        primero = self.client.post('/api/reportes/', self.datos_reporte(), format='json')
        segundo = self.client.post(
            '/api/reportes/', self.datos_reporte(titulo='Otra vez sin luz'), format='json'
        )
        self.assertEqual(primero.status_code, 201)
        self.assertEqual(segundo.status_code, 400)

    # RN-06 (PATCH): transición inválida RECIBIDO -> RESUELTO -> 400
    def test_transicion_de_estado_invalida(self):
        reporte = self.crear_reporte()
        self.usar_token(self.operador)
        respuesta = self.client.patch(
            f'/api/reportes/{reporte.pk}/', {'estado': 'RESUELTO'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 400)

    # RN-06 y RN-07 (PATCH): EN_PROCESO -> RESUELTO guarda la fecha; luego queda cerrado
    def test_resolver_reporte_y_bloquear_cambios(self):
        reporte = self.crear_reporte(estado='EN_PROCESO')
        self.usar_token(self.operador)
        respuesta = self.client.patch(
            f'/api/reportes/{reporte.pk}/', {'estado': 'RESUELTO'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertIsNotNone(respuesta.data['fecha_resolucion'])

        # Ya cerrado: cualquier cambio se rechaza
        respuesta = self.client.patch(
            f'/api/reportes/{reporte.pk}/', {'titulo': 'Cambio tardío'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 400)

    # PATCH del mismo reporte no se bloquea a sí mismo con la regla de duplicados
    def test_patch_no_se_bloquea_a_si_mismo(self):
        reporte = self.crear_reporte()
        self.usar_token(self.operador)
        respuesta = self.client.patch(
            f'/api/reportes/{reporte.pk}/', {'direccion': 'Frente a la iglesia'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 200)

    # Filtro combinado, búsqueda y paginación
    def test_filtros_busqueda_y_paginacion(self):
        for numero in range(7):
            self.crear_reporte(
                titulo=f'Poste caído {numero}', distrito=f'Distrito {numero}', estado='EN_PROCESO'
            )
        self.crear_reporte(titulo='Otro problema', distrito='Esparza')

        respuesta = self.client.get(
            f'/api/reportes/?estado=EN_PROCESO&institucion={self.institucion.pk}&buscar=poste&page=1'
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 7)
        self.assertEqual(len(respuesta.data['results']), 5)

    # Consultar un id inexistente -> 404
    def test_reporte_inexistente_devuelve_404(self):
        respuesta = self.client.get('/api/reportes/99999/')
        self.assertEqual(respuesta.status_code, 404)

    # Permisos: estadísticas solo admin (ciudadano 403, admin 200)
    def test_estadisticas_solo_administrador(self):
        self.crear_reporte()
        respuesta = self.client.get('/api/reportes/estadisticas/')
        self.assertEqual(respuesta.status_code, 403)

        admin = User.objects.create_superuser(
            username='admin_pruebas', email='admin@example.com', password='ClaveSegura123!'
        )
        self.usar_token(admin)
        respuesta = self.client.get('/api/reportes/estadisticas/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['total_reportes'], 1)

    # Perfil: devuelve el rol según el grupo
    def test_perfil_devuelve_rol(self):
        respuesta = self.client.get('/api/perfil/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['rol'], 'Ciudadano')
