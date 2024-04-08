from django.urls import path
from .views import obtener_salas_disponibles, crear_reservas_por_defecto, reservar_sala, mis_reservas

urlpatterns = [
    path('', obtener_salas_disponibles, name='lista_salas'),
    path('crear_reservas/', crear_reservas_por_defecto, name='crear_reservas'),
    path('reservar/', reservar_sala, name='reservar'),
    path('mis_reservas/', mis_reservas, name='mis_reservas'),

]