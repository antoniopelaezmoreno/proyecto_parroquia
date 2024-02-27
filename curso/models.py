from django.db import models

# Create your models here.
class Curso(models.Model):
    curso = models.CharField(max_length=20, unique=True, default=" ")

    def __str__(self):
        return self.curso
    