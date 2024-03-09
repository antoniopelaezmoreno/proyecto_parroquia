from django.urls import path
from .views import crear_sesion, listar_sesiones, pasar_lista,tabla_asistencias_grupo, tabla_asitencias_coord, tabla_asistencias_admin

urlpatterns = [
    path('crear', crear_sesion, name='crear_sesion'),
    path('listar', listar_sesiones, name='listar_sesiones'),
    path('pasar_lista/<int:sesionid>', pasar_lista, name='pasar_lista'),
    path('tabla_asistencia_grupo', tabla_asistencias_grupo, name='tabla_asistencias_grupo'),
    path('tabla_asistencia_coord', tabla_asitencias_coord, name='tabla_asistencias_coord'),
    path('tabla_asistencia_admin/<str:ciclo>', tabla_asistencias_admin, name='tabla_asistencias_admin')


]