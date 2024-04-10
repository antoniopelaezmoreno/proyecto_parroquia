from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Catecumeno
from notificacion.models import Notificacion
from custom_user.models import CustomUser

@receiver(post_save, sender=Catecumeno)
def crear_notificacion_nuevo_catecumeno(sender, instance, created, **kwargs):
    if created:
        ciclo_coordinador = instance.ciclo
        coordinador = CustomUser.objects.filter(ciclo=ciclo_coordinador, is_coord=True).first()
        if coordinador:
            mensaje = f"Se ha creado un nuevo catecúmeno: {instance.nombre} {instance.apellidos}"
            notificacion = Notificacion(mensaje=mensaje)
            notificacion.destinatario = coordinador
            notificacion.save()

