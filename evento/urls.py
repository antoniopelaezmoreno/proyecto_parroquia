from django.urls import path
from .views import crear_evento, nuevo_evento, obtener_eventos

urlpatterns = [
    path('crear/', crear_evento, name='crear_evento'),
    path('nuevo/', nuevo_evento, name='nuevo_evento'),
    path('obtener_eventos/', obtener_eventos, name='obtener_eventos')
]