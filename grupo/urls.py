from django.urls import path
from .views import crear_grupo, crear_grupo_admin, obtener_miembros_de_grupos

urlpatterns = [
    path('crear_grupo/', crear_grupo, name='crear_grupo'),
    path('crear_grupo/<str:ciclo>', crear_grupo_admin, name='crear_grupo_admin'),
    path('miembros', obtener_miembros_de_grupos, name='obtener_miembros_de_grupos')
]