from django.db import models

from custom_user.models import CustomUser
from catecumeno.models import Catecumeno
# Create your models here.
class Grupo(models.Model):
    catequista1 = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name='catequista1', null=True, blank=True)
    catequista2 = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name='catequista2', null=True, blank=True)
    ciclo = models.CharField(max_length=20, choices=Catecumeno.CicloChoices.choices, default = Catecumeno.CicloChoices.POSCO_1)

    def __str__(self):
        if self.catequista1 and self.catequista2:
            return "Grupo de " +self.catequista1.nombre +" y " + self.catequista2.nombre
        elif self.catequista1 and not self.catequista2:
            return "Grupo de " + self.catequista1.nombre + " y Catequista 2"
        elif not self.catequista1 and self.catequista2:
            return "Grupo de Catequista 1 y " + self.catequista2.nombre
        else:
            return "Grupo de Catequista 1 y Catequista 2"
        
    def miembros(self):
        return Catecumeno.objects.filter(grupo=self)
        
