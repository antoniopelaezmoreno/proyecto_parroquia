from django.db import models
from custom_user.models import CustomUser

class Notificacion(models.Model):
    mensaje = models.CharField(max_length=255)
    destinatarios = models.ManyToManyField(CustomUser, related_name='notificaciones')
    visto = models.BooleanField(default=False)

    def __str__(self):
        return self.mensaje
