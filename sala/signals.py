from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SolicitudReserva
from notificacion.models import Notificacion
from custom_user.models import CustomUser

@receiver(post_save, sender=SolicitudReserva)
def crear_notificacion_nueva_solicitud(sender, instance, created, **kwargs):
    if created:
        admin = CustomUser.objects.filter(is_superuser=True).first()
        if admin:
            mensaje = f"Hay una nueva solicitud de reserva para la sala {instance.sala} por {instance.usuario}"
            notificacion = Notificacion(mensaje=mensaje)
            notificacion.save()
            notificacion.destinatarios.set([admin])
    else:
        if instance.estado == SolicitudReserva.EstadoChoices.ACEPTADA:
            mensaje = f"Tu solicitud de reserva para la sala {instance.sala} ha sido aceptada."
            
        elif instance.estado == SolicitudReserva.EstadoChoices.RECHAZADA:
            mensaje = f"Tu solicitud de reserva para la sala {instance.sala} ha sido rechazada."

        notificacion = Notificacion(mensaje=mensaje)
        notificacion.save()
        notificacion.destinatarios.set([instance.usuario])


