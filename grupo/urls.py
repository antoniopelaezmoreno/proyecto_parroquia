from django.urls import path
from .views import crear_grupo, crear_grupo_admin,ag, ajax_obtener_catequistas, panel_grupos, editar_grupo, eliminar_grupo

urlpatterns = [
    path('crear/', crear_grupo, name='crear_grupo'),
    path('crear_grupo/', crear_grupo_admin, name='crear_grupo_admin'),
    path('editar/<int:grupo_id>', editar_grupo, name='editar_grupo'),
    path('eliminar/<int:grupo_id>', eliminar_grupo, name='eliminar_grupo'),
    path('prueba', ag, name='ag'),
    path('ajax/obtener_catequistas/', ajax_obtener_catequistas, name='ajax_obtener_catequistas'),
    path('', panel_grupos, name='panel_grupos')

]