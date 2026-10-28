from django.contrib.auth.models import Group, Permission, User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from categorias.models import Categoria
from instituciones.models import Institucion
from reportes.models import Reporte
from .models import Seguimiento


class SeguimientosAPITests(APITestCase):
    def setUp(self):
        institucion = Institucion.objects.create(
            nombre='Acueductos y Alcantarillados', siglas='AYA', telefono='2242-5000'
        )
        categoria = Categoria.objects.create(nombre='Sin agua', institucion=institucion)
        ciudadano = User.objects.create_user(username='ciudadano', password='ClaveSegura123!')
        self.reporte = Reporte.objects.create(
            titulo='Sin agua potable',
            descripcion='No llega agua desde hace dos días.',
            categoria=categoria,
            ciudadano=ciudadano,
            distrito='Chacarita',
            direccion='Calle principal',
        )

        # Operador con add_seguimiento y change_seguimiento
        grupo = Group.objects.create(name='Operadores')
        grupo.permissions.set(Permission.objects.filter(
            content_type__app_label='seguimientos',
            codename__in=['add_seguimiento', 'change_seguimiento'],
        ))
        self.operador = User.objects.create_user(username='operador', password='ClaveSegura123!')
        self.operador.groups.add(grupo)
        self.ciudadano = ciudadano

        token, _ = Token.objects.get_or_create(user=self.operador)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def datos_seguimiento(self, **cambios):
        datos = {
            'reporte': self.reporte.pk,
            'tipo': 'INSPECCION',
            'comentario': 'Cuadrilla revisó la tubería principal.',
        }
        datos.update(cambios)
        return datos

    # CRUD: el operador registra un seguimiento -> 201 y el reporte pasa a EN_PROCESO
    def test_operador_registra_seguimiento(self):
        respuesta = self.client.post('/api/seguimientos/', self.datos_seguimiento(), format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['operador'], self.operador.pk)
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.estado, 'EN_PROCESO')

    # RN-08: no se registran seguimientos en un reporte cerrado -> 400
    def test_reporte_cerrado_no_admite_seguimientos(self):
        self.reporte.estado = 'RESUELTO'
        self.reporte.save()
        respuesta = self.client.post('/api/seguimientos/', self.datos_seguimiento(), format='json')
        self.assertEqual(respuesta.status_code, 400)

    # RN-08 (PATCH): comentario demasiado corto -> 400
    def test_patch_comentario_corto_devuelve_400(self):
        seguimiento = Seguimiento.objects.create(
            reporte=self.reporte, operador=self.operador, comentario='Revisión inicial'
        )
        respuesta = self.client.patch(
            f'/api/seguimientos/{seguimiento.pk}/', {'comentario': 'ok'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 400)

    # Permisos: un ciudadano sin add_seguimiento -> 403
    def test_ciudadano_no_registra_seguimiento(self):
        token, _ = Token.objects.get_or_create(user=self.ciudadano)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        respuesta = self.client.post('/api/seguimientos/', self.datos_seguimiento(), format='json')
        self.assertEqual(respuesta.status_code, 403)
