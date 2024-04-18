from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Evento
from notificacion.models import Notificacion
from custom_user.models import CustomUser

@receiver(post_save, sender=Evento)
def crear_notificacion_nuevo_evento(sender, instance, created, **kwargs):
    if not created:
        participantes = instance.participantes.all()
        if participantes:
            for participante in participantes:
                mensaje = f"Se te ha invitado a un nuevo evento: {instance.nombre}"
                notificacion = Notificacion(mensaje=mensaje)
                notificacion.destinatario = participante
                notificacion.save()

