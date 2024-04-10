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
            notificacion1 = Notificacion(mensaje=mensaje)
            notificacion1.destinatario=catequista1
            notificacion1.save()
            notificacion2 = Notificacion(mensaje=mensaje)
            notificacion2.destinatario=catequista2
            notificacion2.save()