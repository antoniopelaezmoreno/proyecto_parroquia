from django.apps import AppConfig


class SalaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sala'

    def ready(self):
        import sala.signals
