from django.apps import AppConfig


class SolicitudCatequistaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solicitud_catequista'

    def ready(self):
        import solicitud_catequista.signals
