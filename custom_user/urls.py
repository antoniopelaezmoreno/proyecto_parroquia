from django.urls import path
from .views import iniciar_sesion, cerrar_sesion, crear_usuario_desde_solicitud, listar_catequistas
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('login', LoginView.as_view(), name='iniciar_sesion'),
    path('logout', cerrar_sesion, name='cerrar_sesion'),
    path('new/<int:id>/<str:ciclo>', crear_usuario_desde_solicitud, name='crear_usuario_desde_solicitud'),
    path('listar', listar_catequistas, name='listar_catequistas'),

]