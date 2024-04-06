from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grupo
from notificacion.models import Notificacion
from custom_user.models import CustomUser

@receiver(post_save, sender=Grupo)
def crear_notificacion_nuevo_grupo(sender, instance, created, **kwargs):
    if not created:
        catequista1 = instance.catequista1
        catequista2 = instance.catequista2
        if catequista1 and catequista2:
            mensaje = "Se te ha asignado a un grupo"
            notificacion = Notificacion(mensaje=mensaje)
            notificacion.save()
            notificacion.destinatarios.set([catequista1, catequista2])