from django.urls import path
from .views import iniciar_sesion, cerrar_sesion
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('login', LoginView.as_view(), name='iniciar_sesion'),
    path('logout', cerrar_sesion, name='cerrar_sesion'),
]