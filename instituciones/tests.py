from django.contrib.auth.models import Permission, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from categorias.models import Categoria
from .models import Institucion


class InstitucionesAPITests(APITestCase):
    def setUp(self):
        # Usuario con permisos de modelo sobre instituciones
        self.usuario = User.objects.create_user(
            username='encargado', password='ClaveSegura123!'
        )
        permisos = Permission.objects.filter(
            content_type__app_label='instituciones',
            codename__in=['add_institucion', 'change_institucion', 'delete_institucion'],
        )
        self.usuario.user_permissions.set(permisos)
        token, _ = Token.objects.get_or_create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def datos_institucion(self, nombre='Acueductos y Alcantarillados', siglas='AYA'):
        return {
            'nombre': nombre,
            'siglas': siglas,
            'telefono': '2242-5000',
            'email': 'contacto@aya.example.com',
            'activo': True,
        }

    # CRUD: crear institución -> 201
    def test_crear_institucion(self):
        respuesta = self.client.post('/api/instituciones/', self.datos_institucion(), format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Institucion.objects.count(), 1)

    # Regla RN-01: siglas duplicadas (aunque cambie mayúscula/minúscula) -> 400
    def test_rechaza_siglas_duplicadas(self):
        self.client.post('/api/instituciones/', self.datos_institucion(), format='json')
        respuesta = self.client.post(
            '/api/instituciones/',
            self.datos_institucion(nombre='Otra institución', siglas=' aya '),
            format='json',
        )
        self.assertEqual(respuesta.status_code, 400)

    # Permisos: la consulta es pública (sin token) -> 200
    def test_listado_publico(self):
        self.client.credentials()
        respuesta = self.client.get('/api/instituciones/')
        self.assertEqual(respuesta.status_code, 200)

    # Permisos: crear sin token -> 401
    def test_crear_sin_token_devuelve_401(self):
        self.client.credentials()
        respuesta = self.client.post('/api/instituciones/', self.datos_institucion(), format='json')
        self.assertEqual(respuesta.status_code, 401)

    # Permisos: con token pero sin permiso de modelo -> 403
    def test_crear_sin_permiso_devuelve_403(self):
        otro = User.objects.create_user(username='sin_permiso', password='ClaveSegura123!')
        token, _ = Token.objects.get_or_create(user=otro)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        respuesta = self.client.post('/api/instituciones/', self.datos_institucion(), format='json')
        self.assertEqual(respuesta.status_code, 403)

    # RN-11: no se elimina una institución con categorías -> 409
    def test_no_elimina_institucion_con_categorias(self):
        institucion = Institucion.objects.create(
            nombre='Compañía Nacional de Fuerza y Luz', siglas='CNFL', telefono='2295-5000'
        )
        Categoria.objects.create(nombre='Sin electricidad', institucion=institucion)
        respuesta = self.client.delete(f'/api/instituciones/{institucion.pk}/')
        self.assertEqual(respuesta.status_code, 409)
        self.assertTrue(Institucion.objects.filter(pk=institucion.pk).exists())

    # CRUD: eliminar institución sin categorías -> 204
    def test_eliminar_institucion(self):
        institucion = Institucion.objects.create(
            nombre='Institución temporal', siglas='TMP', telefono='2222-2222'
        )
        respuesta = self.client.delete(f'/api/instituciones/{institucion.pk}/')
        self.assertEqual(respuesta.status_code, 204)
        self.assertFalse(Institucion.objects.filter(pk=institucion.pk).exists())
