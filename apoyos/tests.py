from django.contrib.auth.models import Group, Permission, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from categorias.models import Categoria
from instituciones.models import Institucion
from reportes.models import Reporte
from .models import Apoyo


class ApoyosAPITests(APITestCase):
    def setUp(self):
        institucion = Institucion.objects.create(
            nombre='Ministerio de Obras Públicas y Transportes', siglas='MOPT', telefono='2523-2000'
        )
        categoria = Categoria.objects.create(
            nombre='Hueco en carretera', institucion=institucion, prioridad_base='MEDIA'
        )

        # Grupo Ciudadanos con add_apoyo y delete_apoyo
        self.grupo = Group.objects.create(name='Ciudadanos')
        self.grupo.permissions.set(Permission.objects.filter(
            content_type__app_label='apoyos', codename__in=['add_apoyo', 'delete_apoyo'],
        ))

        self.autor = self.crear_ciudadano('autor')
        self.vecino = self.crear_ciudadano('vecino')
        self.reporte = Reporte.objects.create(
            titulo='Hueco enorme',
            descripcion='Hueco profundo en plena vía, peligroso para motos.',
            categoria=categoria,
            ciudadano=self.autor,
            distrito='Barranca',
            direccion='Frente al supermercado',
        )
        self.usar_token(self.vecino)

    def crear_ciudadano(self, username):
        usuario = User.objects.create_user(username=username, password='ClaveSegura123!')
        usuario.groups.add(self.grupo)
        return usuario

    def usar_token(self, usuario):
        token, _ = Token.objects.get_or_create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # CRUD: un vecino apoya el reporte -> 201
    def test_apoyar_reporte(self):
        respuesta = self.client.post('/api/apoyos/', {'reporte': self.reporte.pk}, format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['ciudadano'], self.vecino.pk)

    # RN-10: apoyar dos veces el mismo reporte -> 409
    def test_apoyo_duplicado_devuelve_409(self):
        self.client.post('/api/apoyos/', {'reporte': self.reporte.pk}, format='json')
        respuesta = self.client.post('/api/apoyos/', {'reporte': self.reporte.pk}, format='json')
        self.assertEqual(respuesta.status_code, 409)

    # RN-09: no se apoya el propio reporte -> 400
    def test_no_apoya_su_propio_reporte(self):
        self.usar_token(self.autor)
        respuesta = self.client.post('/api/apoyos/', {'reporte': self.reporte.pk}, format='json')
        self.assertEqual(respuesta.status_code, 400)

    # Decisión automática: con 3 apoyos el reporte sube a prioridad ALTA
    def test_tres_apoyos_suben_prioridad(self):
        for nombre in ['vecino', 'vecina2', 'vecino3']:
            usuario = self.vecino if nombre == 'vecino' else self.crear_ciudadano(nombre)
            self.usar_token(usuario)
            self.client.post('/api/apoyos/', {'reporte': self.reporte.pk}, format='json')
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.prioridad, 'ALTA')

    # Permisos: no se puede eliminar el apoyo de otro ciudadano -> 403
    def test_no_elimina_apoyo_ajeno(self):
        apoyo = Apoyo.objects.create(reporte=self.reporte, ciudadano=self.vecino)
        otro = self.crear_ciudadano('otro')
        self.usar_token(otro)
        respuesta = self.client.delete(f'/api/apoyos/{apoyo.pk}/')
        self.assertEqual(respuesta.status_code, 403)

    # CRUD: el ciudadano elimina su propio apoyo -> 204
    def test_elimina_su_apoyo(self):
        apoyo = Apoyo.objects.create(reporte=self.reporte, ciudadano=self.vecino)
        respuesta = self.client.delete(f'/api/apoyos/{apoyo.pk}/')
        self.assertEqual(respuesta.status_code, 204)
