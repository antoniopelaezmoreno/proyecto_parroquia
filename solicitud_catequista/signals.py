from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SolicitudCatequista
from notificacion.models import Notificacion
from custom_user.models import CustomUser

@receiver(post_save, sender=SolicitudCatequista)
def crear_notificacion_nueva_solicitud_catequista(sender, instance, created, **kwargs):
    if created:
        admin = CustomUser.objects.filter(is_superuser=True).first()
        if admin:
            mensaje = f"Hay una nueva solicitud de catequista: {instance.nombre} {instance.apellidos}"
            notificacion = Notificacion(mensaje=mensaje)
            notificacion.save()
            notificacion.destinatarios.set([admin])