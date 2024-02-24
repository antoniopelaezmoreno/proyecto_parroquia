from django.db import models


class Catecumeno(models.Model):
    class CicloChoices(models.TextChoices):
        POSCO_1 = 'posco_1', 'Poscomunión 1'
        POSCO_2 = 'posco_2', 'Poscomunión 2'
        POSCO_3 = 'posco_3', 'Poscomunión 3'
        POSCO_4 = 'posco_4', 'Poscomunión 4'
        GRUPOS_JUVENILES_1 = 'gr_juv_1', 'Grupos Juveniles 1'
        GRUPOS_JUVENILES_2 = 'gr_juv_2', 'Grupos Juveniles 2'
        CATECUMENADOS_1 = 'catequmenados_1', 'Catecumenados 1'
        CATECUMENADOS_2 = 'catequmenados_2', 'Catecumenados 2'
        CATECUMENADOS_3 = 'catequmenados_3', 'Catecumenados 3'


    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    dni = models.CharField(max_length=10)
    ciclo = models.CharField(max_length=20, choices=CicloChoices.choices, default=CicloChoices.POSCO_1)
    nombre_madre = models.CharField(max_length=100)
    apellidos_madre = models.CharField(max_length=100)
    email_madre = models.EmailField(max_length=100)
    dni_madre = models.CharField(max_length=10)
    nombre_padre = models.CharField(max_length=100)
    apellidos_padre = models.CharField(max_length=100)
    email_padre = models.EmailField(max_length=100)
    dni_padre = models.CharField(max_length=10)
    preferencias = models.CharField(max_length=200)
    preferencias_procesadas =models.ManyToManyField('self', related_name='preferencias_procesadas_rel', symmetrical=False)
    foto = models.ImageField(upload_to='autorizaciones/', blank=True, null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellidos