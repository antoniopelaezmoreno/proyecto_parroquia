from django.test import TestCase
from django.urls import reverse
from solicitud_catequista.models import SolicitudCatequista
from custom_user.models import CustomUser

class TestsUnitariosCrearSolicitudCatequista(TestCase):
    
    def test_crear_solicitud_catequista_exitosa(self):
        data = {
            'nombre': 'Juan',
            'apellidos': 'Perez',
            'email': 'juan@example.com',
            'disponibilidad': 'Tardes',
            'preferencias': 'No tengo preferencias',
        }
        response = self.client.post(reverse('crear_solicitud_catequista'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SolicitudCatequista.objects.filter(email='juan@example.com').exists())

    def test_crear_solicitud_catequista_con_email_existente(self):
        CustomUser.objects.create_user(email='pedro@example.com', password='test123')
        
        data = {
            'nombre': 'Pedro',
            'apellidos': 'Lopez',
            'email': 'pedro@example.com',
            'disponibilidad': 'Tardes',
            'preferencias': 'No tengo preferencias',
        }
        response = self.client.post(reverse('crear_solicitud_catequista'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SolicitudCatequista.objects.filter(email='pedro@example.com').exists())
        self.assertIn('email', response.json()['errors'])

class TestUnitariosAsignarCatequistas(TestCase):

    def setUp(self):
        self.catequista = CustomUser.objects.create_user(email='user@example.com', password='password')


    def test_acceso_denegado_usuario_no_superuser(self):
        # Probar el acceso denegado para un usuario que no es superadmin
        self.client.force_login(self.catequista)
        response = self.client.get(reverse('asignar_catequistas'))

        self.assertEqual(response.status_code, 302)  # Redireccionado a la página de permisos insuficientes



