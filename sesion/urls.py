from django.urls import path
from .views import crear_sesion, crear_sesion_admin, listar_sesiones

urlpatterns = [
    path('crear', crear_sesion, name='crear_sesion'),
    path('crear/<str:ciclo>', crear_sesion_admin, name='crear_sesion_admin'),
    path('listar', listar_sesiones, name='listar_sesiones'),


]