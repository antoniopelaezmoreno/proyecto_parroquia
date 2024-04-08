from django.db import models
from custom_user.models import CustomUser

# Create your models here.
class Sala(models.Model):
    nombre = models.CharField(max_length=100, unique=True, error_messages={'unique': 'Ya existe una sala con este nombre.'})
    requiere_aprobacion = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f'{self.sala} reservada por {self.usuario} para el {self.fecha} de {self.hora_inicio} a {self.hora_fin}'
    
class SolicitudReserva(models.Model):
    class EstadoChoices(models.TextChoices):
        ACEPTADA = 'aceptada', 'Aceptada'
        RECHAZADA = 'rechazada', 'Rechazada'
        PENDIENTE = 'pendiente', 'Pendiente'

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=100, choices= EstadoChoices.choices ,default=EstadoChoices.PENDIENTE)

    def __str__(self):
        return f'Solicitud de reserva de {self.sala} por {self.usuario} para el {self.fecha} de {self.hora_inicio} a {self.hora_fin}'