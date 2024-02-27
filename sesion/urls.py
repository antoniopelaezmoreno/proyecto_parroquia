from django.urls import path
from .views import crear_sesion, crear_sesion_admin

urlpatterns = [
    path('crear', crear_sesion, name='crear_sesion'),
    path('crear/<str:ciclo>', crear_sesion_admin, name='crear_sesion_admin'),


]