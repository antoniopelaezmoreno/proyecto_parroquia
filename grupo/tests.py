from django.test import TestCase, Client
from django.urls import reverse
from custom_user.models import CustomUser
from grupo.models import Grupo

class TestUnitariosCrearGrupoAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('crear_grupo_admin')
        self.superuser = CustomUser.objects.create_superuser(email='admin@example.com', password='admin')
        self.catequista1 = CustomUser.objects.create_user(email='catequista1@example.com', password='catequista1')
        self.catequista2 = CustomUser.objects.create_user(email='catequista2@example.com', password='catequista2')

    def test_crear_grupo_admin_success(self):
        self.client.login(email='admin@example.com', password='admin')
        response = self.client.post(self.url, {
            'ciclo': 'posco_1',
            'catequista1': self.catequista1.id,
            'catequista2': self.catequista2.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(Grupo.objects.count(), 1)
        grupo = Grupo.objects.first()
        self.assertEqual(grupo.ciclo, 'posco_1')
        self.assertEqual(grupo.catequista1, self.catequista1)
        self.assertEqual(grupo.catequista2, self.catequista2)
        self.client.logout()

    
    def test_crear_grupo_admin_not_superuser(self):
        self.client.login(email='catequista1@example.com', password='catequista1')
        response = self.client.get(self.url)
        print(response)
        self.assertEqual(Grupo.objects.count(), 0)
        self.assertEqual(response.url, '/403')
        self.client.logout()
        

class TestsUnitariosEditarGrupo(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword', is_coord=True)
        self.grupo = Grupo.objects.create(ciclo='posco_1')
    
    def test_editar_grupo_success(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('editar_grupo', args=[self.grupo.id]), {'ciclo': 'posco_1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/grupo?ciclo=posco_1')
        self.grupo.refresh_from_db()
        self.assertEqual(self.grupo.ciclo, 'posco_1')
    
    def test_editar_grupo_invalid_group(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('editar_grupo', args=[999]), {'ciclo': 'posco_1'})
        self.assertEqual(response.status_code, 404)
        self.grupo.refresh_from_db()
        self.assertEqual(self.grupo.ciclo, 'posco_1')