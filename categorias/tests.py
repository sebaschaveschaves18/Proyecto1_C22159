from django.contrib.auth.models import Permission, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from instituciones.models import Institucion
from .models import Categoria


class CategoriasAPITests(APITestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre='Ministerio de Obras Públicas y Transportes', siglas='MOPT', telefono='2523-2000'
        )
        # Usuario con permisos de modelo sobre categorías
        self.usuario = User.objects.create_user(
            username='encargado', password='ClaveSegura123!'
        )
        permisos = Permission.objects.filter(
            content_type__app_label='categorias',
            codename__in=['add_categoria', 'change_categoria', 'delete_categoria'],
        )
        self.usuario.user_permissions.set(permisos)
        token, _ = Token.objects.get_or_create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # CRUD: actualizar con PATCH -> 200
    def test_actualizar_categoria_con_patch(self):
        categoria = Categoria.objects.create(nombre='Hueco en carretera', institucion=self.institucion)
        respuesta = self.client.patch(
            f'/api/categorias/{categoria.pk}/', {'prioridad_base': 'ALTA'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['prioridad_base'], 'ALTA')

    # RN-02: no se asigna una institución inactiva -> 400
    def test_rechaza_institucion_inactiva(self):
        self.institucion.activo = False
        self.institucion.save()
        respuesta = self.client.post(
            '/api/categorias/',
            {'nombre': 'Puente dañado', 'institucion': self.institucion.pk},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 400)

    # Filtro combinado (?institucion=&prioridad=) y paginación de 5
    def test_filtro_combinado_y_paginacion(self):
        otra = Institucion.objects.create(nombre='Municipalidad', siglas='MUNI', telefono='2661-0000')
        for numero in range(7):
            Categoria.objects.create(
                nombre=f'Categoria {numero}', institucion=self.institucion, prioridad_base='ALTA'
            )
        Categoria.objects.create(nombre='Basura', institucion=otra, prioridad_base='ALTA')

        self.client.credentials()
        respuesta = self.client.get(
            f'/api/categorias/?institucion={self.institucion.pk}&prioridad=ALTA&page=1'
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 7)
        self.assertEqual(len(respuesta.data['results']), 5)

    # Consultar un id inexistente -> 404
    def test_categoria_inexistente_devuelve_404(self):
        respuesta = self.client.get('/api/categorias/99999/')
        self.assertEqual(respuesta.status_code, 404)
