from django.urls import path
from .views import crear_catecumeno, listar_catecumenos, asociar_preferencias, asignar_catecumenos_a_grupo

urlpatterns = [
    path('crear/', crear_catecumeno, name='crear_catecumeno'),
    path('listar/', listar_catecumenos, name='listar_catecumenos'),
    path('asociar_preferencias/<str:ciclo>/', asociar_preferencias, name='asociar_preferencias'),
    path('asignar_a_grupo/', asignar_catecumenos_a_grupo, name='asignar_catecumenos_a_grupo'),


]
