from django.urls import path
from .views import bandeja_de_entrada, enviar_correo, marcar_mensaje_visto, obtener_detalles_mensaje,obtener_detalles_mensaje_enviado,bandeja_salida, pantalla_enviar_correo

urlpatterns = [
    path('inbox', bandeja_de_entrada, name='inbox'),
    path('enviar_correo', enviar_correo, name='enviar_correo'),
    path('visto/<str:message_id>', marcar_mensaje_visto, name='marcar_mensaje_visto'),
    path('detalles/<str:mensaje_id>', obtener_detalles_mensaje, name='detalles_mensaje'),
    path('detalles_enviado/<str:mensaje_id>', obtener_detalles_mensaje_enviado, name='detalles_mensaje_enviado'),
    path('outbox', bandeja_salida, name='outbox'),
    path('pantalla_enviar_correo/<int:catecumeno_id>', pantalla_enviar_correo, name='pantalla_enviar_correo'),
]
