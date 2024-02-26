from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
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

    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    is_coord = models.BooleanField(default=False)
    ciclo = models.CharField(max_length=20, choices=CicloChoices.choices, default=CicloChoices.POSCO_1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.first_name + ' ' + self.last_name