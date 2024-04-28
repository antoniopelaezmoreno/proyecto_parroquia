from django.urls import path
from .views import marcar_notificacion_vista

urlpatterns = [
    path('marcar/<int:notificacion_id>/', marcar_notificacion_vista, name='marcar_notificacion_vista'),
]