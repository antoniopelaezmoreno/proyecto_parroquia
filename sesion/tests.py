from django.test import TestCase
from django.urls import reverse
from sesion.models import Sesion
import datetime as dt
from custom_user.models import CustomUser
from curso.models import Curso
from grupo.models import Grupo
from catecumeno.models import Catecumeno

class SesionTestCase(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(curso='23-24')
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword', ciclo='posco_1')
        self.sesion = Sesion.objects.create(titulo='Test Sesion', descripcion='This is a test session', fecha='2030-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), ciclo='posco_1', curso=self.curso)
        self.client.force_login(self.user)

    #Unitario
    def test_modelo_sesion(self):
        sesion = Sesion.objects.create(titulo='Crear Sesion', descripcion='This is a test session', fecha='2040-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), ciclo='posco_1', curso=self.curso)
        self.assertEqual(sesion.titulo, 'Crear Sesion')
        self.assertEqual(sesion.descripcion, 'This is a test session')

    def test_editar_sesion(self):
        data = {
            'titulo': 'Test Sesion',
            'descripcion': 'Description modified',
            'fecha': '2030-01-01',
            'hora_inicio': dt.time(11,0),
            'hora_fin': dt.time(12,0),
        }
        response = self.client.post(reverse('editar_sesion', args=[self.sesion.id]), data)

        self.assertEqual(response.status_code, 302)
        self.sesion.refresh_from_db()
        self.assertEqual(self.sesion.titulo, 'Test Sesion')
        self.assertEqual(self.sesion.descripcion, 'Description modified')

class PasarListaTestCase(TestCase):
    def setUp(self):
        curso = Curso.objects.create(curso='23-24')
        self.catequista1 = CustomUser.objects.create_user(email='testuser@email.com', password='testpassword')
        self.catequista2 = CustomUser.objects.create_user(email='testuser2@email.com', password='testpassword')
        self.grupo = Grupo.objects.create(catequista1=self.catequista1, catequista2=self.catequista2, ciclo='posco_1')
        self.catecumeno = Catecumeno.objects.create(nombre='Test Catecumeno', apellidos='Test', grupo=self.grupo)
        self.sesion = Sesion.objects.create(titulo='Test Sesion', descripcion='This is a test session', fecha='2024-05-20', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), ciclo='posco_1', curso=curso)
        self.client.force_login(self.catequista1)

    def test_pasar_lista(self):
        response = self.client.post(reverse('pasar_lista', args=[self.sesion.id]), {f'categoria_{self.catecumeno.id}': 'asistente'})
        self.sesion.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.sesion.asistentes.count(), 1)