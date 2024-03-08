from django.urls import path
from .views import crear_sesion, listar_sesiones

urlpatterns = [
    path('crear', crear_sesion, name='crear_sesion'),
    path('listar', listar_sesiones, name='listar_sesiones'),


]