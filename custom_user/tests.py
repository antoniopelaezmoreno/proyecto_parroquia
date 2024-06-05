from django.test import TestCase
from solicitud_catequista.models import SolicitudCatequista
from custom_user.models import CustomUser
import uuid
from django.urls import reverse


class TestsUnitariosCrearUsuarioDesdeSolicitud(TestCase):

    def setUp(self):
        self.solicitud = SolicitudCatequista.objects.create(
            nombre="Nombre",
            apellidos="Apellidos",
            email="correo@example.com",
            ciclo_asignado="posco_1",
            token = uuid.uuid4()
        )

    def test_crear_usuario_desde_solicitud_post(self):
        # Hacer una solicitud POST a la vista con datos válidos
        data = {
            'password': 'useruser',
            'confirmar_password': 'useruser',
            'telefono': '123456789'
        }
        response = self.client.post(reverse('crear_usuario_desde_solicitud', kwargs={'token': self.solicitud.token}), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login')

        # Verificar que el usuario se ha creado correctamente
        self.assertTrue(CustomUser.objects.filter(email='correo@example.com').exists())

    def test_crear_usuario_desde_solicitud_password(self):
        # Hacer una solicitud POST a la vista con datos válidos
        data = {
            'password': 'useruser',
            'confirmar_password': 'user',
            'telefono': '123456789'
        }
        response = self.client.post(reverse('crear_usuario_desde_solicitud', kwargs={'token': self.solicitud.token}), data)
        self.assertEqual(response.status_code, 200)

class TestsUnitariosConvertirCoordinador(TestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(email='admin@gmail.com', password='admin123')
        self.usuario1 = CustomUser.objects.create(email='usuario1@example.com', ciclo='posco_1')
        self.usuario2 = CustomUser.objects.create(email='usuario2@example.com', ciclo='posco_1')
        self.usuario3 = CustomUser.objects.create(email='usuario3@example.com', ciclo='posco_2')

    def test_convertir_a_coordinador(self):

        self.client.force_login(self.superuser)
        data = {
            'cycle_posco_1': self.usuario1.id
        }
        response = self.client.post(reverse('convertir_a_coordinador'), data)
        self.assertEqual(response.status_code, 302)

        self.usuario1.refresh_from_db()
        self.assertTrue(self.usuario1.is_coord)

        user2 = CustomUser.objects.get(email='usuario2@example.com')
        user3 = CustomUser.objects.get(email='usuario3@example.com')
        self.assertFalse(user2.is_coord)
        self.assertFalse(user3.is_coord) 

    def test_renderizar_template(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('convertir_a_coordinador'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crear_coordinadores.html')
        self.assertIn('users_by_cycle', response.context)

        usuarios_por_ciclo = response.context['users_by_cycle']
        self.assertIn(('posco_1', 'Posco 1'), usuarios_por_ciclo)
        self.assertIn(('posco_2', 'Posco 2'), usuarios_por_ciclo)
