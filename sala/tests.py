from django.test import TestCase
from django.urls import reverse
from .models import Sala, Reserva
from custom_user.models import CustomUser
from datetime import datetime, timedelta
import datetime as dt
from unittest.mock import patch
from django.core.exceptions import ValidationError

class SalaTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(email='testuser@example.com', password='testpassword')
        self.sala = Sala.objects.create(nombre='Sala 1')
        self.reserva = Reserva.objects.create(usuario=self.user, sala=self.sala, fecha='2030-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), estado=Reserva.EstadoChoices.ACEPTADA)
        self.client.force_login(self.user)

    #Unitario
    def test_modelo_sala(self):
        sala = Sala.objects.create(nombre='Sala Test')
        self.assertEqual(sala.nombre, 'Sala Test')
        self.assertEqual(sala.requiere_aprobacion, False)

    #Unitario
    def test_modelo_reserva(self):
        reserva = Reserva.objects.create(usuario=self.user, sala=self.sala, fecha='2040-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), estado=Reserva.EstadoChoices.ACEPTADA)
        self.assertEqual(reserva.usuario, self.user)
        self.assertEqual(reserva.fecha, '2040-01-01')

    #Unitario
    def test_estado_opcion_invalida(self):
        reserva = Reserva.objects.create(usuario=self.user, sala=self.sala, fecha='2050-01-01', hora_inicio=dt.time(11,0), hora_fin=dt.time(12,0), estado='opcion_invalida')
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_reservar_sala_success(self):
        response = self.client.post(reverse('reservar'), {
            'sala_id': self.sala.id,
            'fecha': datetime.now().date() + timedelta(days=1),
            'hora_inicio': dt.time(11,0),
            'hora_fin': dt.time(12,0),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mis_reservas'))
        self.assertEqual(Reserva.objects.count(), 2)
        reserva = Reserva.objects.latest('id')
        self.assertEqual(reserva.usuario, self.user)
        self.assertEqual(reserva.sala, self.sala)
        self.assertEqual(reserva.fecha, datetime.now().date() + timedelta(days=1))
        self.assertEqual(reserva.hora_inicio, dt.time(11,0))
        self.assertEqual(reserva.hora_fin, dt.time(12,0))
        self.assertEqual(reserva.estado, Reserva.EstadoChoices.ACEPTADA)

    def test_obtener_salas_disponibles(self):
        data = {
            'fecha': '2030-01-01',
            'hora_inicio': dt.time(10,0),
            'hora_fin': dt.time(12,0)
        }
        response = self.client.post(reverse('lista_salas'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'salas_disponibles.html')
        self.assertContains(response, self.sala.nombre)
        self.assertNotContains(response, 'No hay salas disponibles')

    @patch('django.utils.timezone.now')
    def test_crear_reservas_por_defecto(self, mock_now):
        mock_now.return_value = datetime(2024, 6, 6)

        sala = Sala.objects.create(nombre='Sala 2')
        response = self.client.post(reverse('crear_reservas'), {
            'usuario': self.user.id,
            'sala': sala.id,
            'dia_semana': 4,  # Friday
            'hora_inicio': dt.time(9,0),
            'hora_fin': dt.time(10,0)
        })

        self.assertEqual(response.status_code, 302)

        today = datetime.now().date()
        next_friday = today + timedelta(days=(4 - today.weekday() + 7) % 7)
        
        reservations = Reserva.objects.filter(usuario=self.user, sala=sala, fecha__gte=next_friday)
        self.assertEqual(reservations.count(), 4)

        reservation = reservations.first()
        self.assertEqual(reservation.usuario, self.user)
        self.assertEqual(reservation.sala, sala)
        self.assertEqual(reservation.fecha, next_friday)
        self.assertEqual(reservation.hora_inicio, dt.time(9,0))
        self.assertEqual(reservation.hora_fin, dt.time(10,0))
        self.assertEqual(reservation.estado, Reserva.EstadoChoices.ACEPTADA)
    
    def test_reservar_sala_fecha_pasada(self):
        response = self.client.post(reverse('reservar'), {
            'sala_id': self.sala.id,
            'fecha': '2021-01-01',
            'hora_inicio': '10:00',
            'hora_fin': '12:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'No se puede reservar una sala para una fecha pasada.')
        self.assertEqual(Reserva.objects.count(), 1)
    
    def test_reservar_sala_horas_invalidas(self):
        response = self.client.post(reverse('reservar'), {
            'sala_id': self.sala.id,
            'fecha': datetime.now().date() + timedelta(days=1),
            'hora_inicio': '14:00',
            'hora_fin': '12:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'La hora de inicio debe ser menor a la hora de fin.')
        self.assertEqual(Reserva.objects.count(), 1)

    def test_reservar_sala_solapada(self):
        response = self.client.post(reverse('reservar'), {
            'sala_id': self.sala.id,
            'fecha': '2030-01-01',
            'hora_inicio': dt.time(11,0),
            'hora_fin': dt.time(12,0),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reserva.objects.count(), 1)
    

