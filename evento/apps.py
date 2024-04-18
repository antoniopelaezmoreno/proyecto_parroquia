from django.apps import AppConfig


class EventoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evento'

    def ready(self):
        import evento.signals
