from django.db import models

from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
from curso.models import Curso

# Create your models here.
class Grupo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True)
    catequista1 = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name='catequista1', null=True, blank=True)
    catequista2 = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name='catequista2', null=True, blank=True)
    ciclo = models.CharField(max_length=20, choices=Catecumeno.CicloChoices.choices, default = Catecumeno.CicloChoices.POSCO_1)
    def __str__(self):
        return "Grupo de " +self.catequista1.first_name +" y " + self.catequista2.first_name