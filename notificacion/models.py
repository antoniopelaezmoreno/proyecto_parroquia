from django.db import models
from custom_user.models import CustomUser
from datetime import date

class Notificacion(models.Model):
    mensaje = models.CharField(max_length=255)
    destinatario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='destinatario', null=True, blank=True)
    visto = models.BooleanField(default=False)
    fecha = models.DateField(default=date.today)

    def __str__(self):
        return self.mensaje
