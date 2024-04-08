from django.urls import path
from .views import obtener_salas_disponibles, crear_reservas_por_defecto, reservar_sala, mis_reservas, listar_solicitudes_reserva, aprobar_solicitud_reserva, rechazar_solicitud_reserva, crear_sala

urlpatterns = [
    path('', obtener_salas_disponibles, name='lista_salas'),
    path('crear/', crear_sala, name='crear_sala'),
    path('crear_reservas/', crear_reservas_por_defecto, name='crear_reservas'),
    path('reservar/', reservar_sala, name='reservar'),
    path('mis_reservas/', mis_reservas, name='mis_reservas'),
    path('solicitudes/', listar_solicitudes_reserva, name='solicitudes_reserva'),
    path('aprobar_solicitud/<int:solicitud_id>/', aprobar_solicitud_reserva, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', rechazar_solicitud_reserva, name='rechazar_solicitud'),


]
