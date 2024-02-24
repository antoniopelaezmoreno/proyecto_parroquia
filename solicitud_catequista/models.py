from django.db import models


class SolicitudCatequista(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    disponibilidad = models.CharField(max_length=200)
    preferencias = models.CharField(max_length=200)
    

    def __str__(self):
        return self.nombre + ' ' + self.apellidos