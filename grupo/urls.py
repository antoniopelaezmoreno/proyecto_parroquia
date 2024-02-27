from django.urls import path
from .views import crear_grupo, crear_grupo_admin

urlpatterns = [
    path('crear_grupo/', crear_grupo, name='crear_grupo'),
    path('crear_grupo/<str:ciclo>', crear_grupo_admin, name='crear_grupo_admin'),
]