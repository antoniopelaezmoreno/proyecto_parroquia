from django.urls import path
from .views import bandeja_entrada_familias, bandeja_entrada_catequistas, enviar_correo

urlpatterns = [
    path('inbox_familias', bandeja_entrada_familias, name='bandeja_de_entrada_familias'),
    path('inbox_catequistas', bandeja_entrada_catequistas, name='bandeja_de_entrada_catequistas'),
    path('enviar_correo', enviar_correo, name='enviar_correo'),
]
