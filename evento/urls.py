from django.urls import path
from .views import crear_evento, nuevo_evento

urlpatterns = [
    path('crear/', crear_evento, name='crear_evento'),
    path('nuevo/', nuevo_evento, name='nuevo_evento'),
]