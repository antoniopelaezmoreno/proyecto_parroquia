from django.urls import path
from .views import iniciar_sesion, cerrar_sesion, crear_usuario_desde_solicitud, listar_catequistas, crear_grupo, crear_grupo_admin
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('login', LoginView.as_view(), name='iniciar_sesion'),
    path('logout', cerrar_sesion, name='cerrar_sesion'),
    path('new/<int:id>/<str:ciclo>', crear_usuario_desde_solicitud, name='crear_usuario_desde_solicitud'),
    path('listar', listar_catequistas, name='listar_catequistas'),
    path('crear_grupo/', crear_grupo, name='crear_grupo'),
    path('crear_grupo/<str:ciclo>', crear_grupo_admin, name='crear_grupo_admin'),

]