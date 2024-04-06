from django.apps import AppConfig


class CatecumenoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catecumeno'

    def ready(self):
        import catecumeno.signals
