from django.db import models
from catecumeno.models import Catecumeno
from curso.models import Curso
from drive.models import Archivo

# Create your models here.
class Sesion(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()
    hora_inicio = models.TimeField(default='00:00:00')
    hora_fin = models.TimeField(default='00:00:00')
    ciclo = models.CharField(max_length=20, choices=Catecumeno.CicloChoices.choices, null=True )
    curso= models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    asistentes = models.ManyToManyField(Catecumeno, related_name='sesiones_asistentes')
    justificados = models.ManyToManyField(Catecumeno, related_name='sesiones_justificados')
    ausentes = models.ManyToManyField(Catecumeno, related_name='sesiones_ausentes') 
    files = models.ManyToManyField(Archivo, related_name='sesiones', blank=True)

    def __str__(self):
        return f"Sesión de {self.ciclo} - {self.fecha}"
