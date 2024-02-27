from django.db import models
from catecumeno.models import Catecumeno
from curso.models import Curso

# Create your models here.
class Sesion(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()
    ciclo = models.CharField(max_length=20, choices=Catecumeno.CicloChoices.choices, null=True )
    curso= models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    asistentes = models.ManyToManyField(Catecumeno, related_name='sesiones_asistentes', null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Sesión de {self.ciclo} - {self.fecha}"