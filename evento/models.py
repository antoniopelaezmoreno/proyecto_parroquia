from django.db import models
from sala.models import Sala
from custom_user.models import CustomUser

# Create your models here.
class Evento(models.Model):
    class TIPO_EVENTO(models.TextChoices):
        REUNION = 'reunion', 'Reunión'
        CONVIVENCIA = 'convivencia', 'Convivencia'
        OTRO = 'otro', 'Otro'

    nombre = models.CharField(max_length=75)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    descripcion = models.TextField()
    participantes = models.ManyToManyField(CustomUser, related_name='participantes_rel')
    tipo = models.CharField(max_length=100, choices=TIPO_EVENTO.choices, default=TIPO_EVENTO.REUNION)
    sala_reservada = models.ForeignKey(Sala, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nombre