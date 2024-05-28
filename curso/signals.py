# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Curso
from sesion.models import Sesion


@receiver(post_save, sender=Sesion)
def asignar_curso(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'curso'):
        curso_actual = Curso.objects.latest('id')
        instance.curso = curso_actual
        instance.save()