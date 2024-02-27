from django.db import models
from curso.models import Curso


class SolicitudCatequista(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    disponibilidad = models.CharField(max_length=200)
    preferencias = models.CharField(max_length=200)
    curso= models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return self.nombre + ' ' + self.apellidos