from django.test import TestCase, Client
from django.urls import reverse
from .models import Evento, Sala
from custom_user.models import CustomUser
from datetime import datetime
import datetime as dt
import json


class TestUnitariosEvento(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(email='prueba@example.com', password='useruser', is_coord=True)
        self.superuser = CustomUser.objects.create_superuser(email='superuser@example.com', password='superuser')
        self.sala = Sala.objects.create(nombre='Sala 1', requiere_aprobacion=False)
        self.evento = Evento.objects.create(nombre='Evento de prueba', fecha='2030-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), tipo=Evento.TIPO_EVENTO.REUNION, descripcion='Descripción del evento', sala_reservada=None)
        self.evento.participantes.add(self.user)
        self.client.force_login(self.user)
    
    def test_obtener_eventos(self):
        response = self.client.get(reverse('obtener_eventos'))
        self.assertEqual(response.status_code, 200)
        
        eventos_data = json.loads(response.content)
        self.assertEqual(len(eventos_data), 1)
        
        evento_data = eventos_data[0]
        self.assertEqual(evento_data['id'], self.evento.id)
        self.assertEqual(evento_data['title'], self.evento.nombre)
        self.assertEqual(evento_data['start'], '2030-01-01T11:00:00')
        self.assertEqual(evento_data['end'], '2030-01-01T12:00:00')
        self.assertEqual(evento_data['color'], '#2c36bd')
        self.assertEqual(evento_data['tipo'], 'Evento')
        self.assertEqual(evento_data['description'], self.evento.descripcion)
        self.assertIsNone(evento_data['sala_reservada'])

    def test_crear_evento_post(self):
        data = {
            'fecha': datetime.now().date(),
            'hora_inicio': dt.time(10,0),
            'hora_fin': dt.time(12,0),
            'nombre': 'Evento Test',
            'tipo': Evento.TIPO_EVENTO.REUNION,
            'descripcion': 'Descripción del evento',
            'participantes': [self.user.id],
            'sala_id': self.sala.id
        }
        response = self.client.post(reverse('nuevo_evento'), data)
        evento = Evento.objects.get(nombre='Evento Test')
        self.assertEqual(evento.descripcion, 'Descripción del evento')
        self.assertIn(self.user, evento.participantes.all())