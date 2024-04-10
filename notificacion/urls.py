from django.urls import path
from .views import ver_notificaciones, marcar_notificacion_vista

urlpatterns = [
    path('listar/', ver_notificaciones, name='ver_notificaciones'),
    path('marcar/<int:notificacion_id>/', marcar_notificacion_vista, name='marcar_notificacion_vista'),
]