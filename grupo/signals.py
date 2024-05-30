from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Grupo
from notificacion.models import Notificacion
from django.db.models import F

@receiver(pre_save, sender=Grupo)
def capturar_valores_anteriores(sender, instance, **kwargs):
    # Verificar si es una actualización, ya que no necesitamos hacer nada para nuevas instancias
    if instance.pk:
        try:
            # Obtener la instancia actual de la base de datos
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        
        # Capturar los valores anteriores de los campos catequista1 y catequista2
        instance._old_catequista1_id = old_instance.catequista1_id
        instance._old_catequista2_id = old_instance.catequista2_id
    else:
        instance._old_catequista1_id = None
        instance._old_catequista2_id = None

@receiver(post_save, sender=Grupo)
def crear_notificacion_edicion_grupo(sender, instance, **kwargs):
    # Comparar los valores anteriores con los valores actuales
    if instance.catequista1_id != instance._old_catequista1_id:
        # Los valores han cambiado, por lo tanto, crear las notificaciones
        catequista1 = instance.catequista1
        if catequista1:
            mensaje = "Se te ha asignado a un grupo"
            notificacion1 = Notificacion(mensaje=mensaje)
            notificacion1.destinatario = catequista1
            notificacion1.save()
    if instance.catequista2_id != instance._old_catequista2_id:
        catequista2 = instance.catequista2
        if catequista2:
            mensaje = "Se te ha asignado a un grupo"
            notificacion2 = Notificacion(mensaje=mensaje)
            notificacion2.destinatario = catequista2
            notificacion2.save()
