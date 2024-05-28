from django.db.models.signals import post_save
from django.dispatch import receiver
from notificacion.models import Notificacion
from custom_user.models import CustomUser
from .models import Reserva

@receiver(post_save, sender=Reserva)
def crear_notificacion_nueva_solicitud(sender, instance, created, **kwargs):
    admin = CustomUser.objects.filter(is_superuser=True).first()
    if created:
        if admin:
            if instance.estado == Reserva.EstadoChoices.PENDIENTE:
                mensaje = f"Hay una nueva solicitud de reserva para la sala {instance.sala} por {instance.usuario}"
                notificacion = Notificacion(mensaje=mensaje)
                notificacion.destinatario=admin
                notificacion.save()
    else:
        if instance.estado == Reserva.EstadoChoices.ACEPTADA:
            mensaje = f"Tu solicitud de reserva para la sala {instance.sala} ha sido aceptada."
            
        elif instance.estado == Reserva.EstadoChoices.RECHAZADA:
            mensaje = f"Tu solicitud de reserva para la sala {instance.sala} ha sido rechazada."

        notificacion = Notificacion(mensaje=mensaje)
        notificacion.destinatario=admin
        notificacion.save()


