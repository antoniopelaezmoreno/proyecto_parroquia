from django.urls import path
from .views import cerrar_sesion, crear_usuario_desde_solicitud, listar_catequistas, editar_catequista, convertir_a_coordinador
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('login', LoginView.as_view(), name='iniciar_sesion'),
    path('logout', cerrar_sesion, name='cerrar_sesion'),
    path('editar/<int:id>', editar_catequista, name='editar_catequista'),
    path('new/<uuid:token>', crear_usuario_desde_solicitud, name='crear_usuario_desde_solicitud'),
    path('listar', listar_catequistas, name='listar_catequistas'),
    path('convertir_coordinador', convertir_a_coordinador, name='convertir_a_coordinador'),



]