from django.urls import path
from .views import crear_grupo, crear_grupo_admin,ag, ajax_obtener_catequistas

urlpatterns = [
    path('crear/', crear_grupo, name='crear_grupo'),
    path('crear_grupo/', crear_grupo_admin, name='crear_grupo_admin'),
    path('prueba', ag, name='ag'),
    path('ajax/obtener_catequistas/', ajax_obtener_catequistas, name='ajax_obtener_catequistas'),
]