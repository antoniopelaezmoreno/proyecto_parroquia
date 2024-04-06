from django.urls import path
from .views import obtener_salas_disponibles, crear_reservas_por_defecto

urlpatterns = [
    path('obtener_libres/', obtener_salas_disponibles, name='obtener_libres'),
    path('crear_reservas/', crear_reservas_por_defecto, name='crear_reservas'),
]