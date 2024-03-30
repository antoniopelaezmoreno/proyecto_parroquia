from django.urls import path
from .views import subir_archivo, listar_archivos, crear_carpeta, eliminar_archivo, eliminar_carpeta, mover_archivo, mover_carpeta


urlpatterns = [
    path('subir/', subir_archivo, name='subir_archivo'),
    path('subir/<int:folder_id>', subir_archivo, name='subir_archivo_en_carpeta'),
    path('listar/', listar_archivos, name='listar_archivos'),
    path('listar/<int:folder_id>', listar_archivos, name='listar_archivos_en_carpeta'),
    path('crear_carpeta', crear_carpeta, name='crear_carpeta'),
    path('crear_carpeta/<int:folder_id>', crear_carpeta, name='crear_carpeta_en_carpeta'),
    path('eliminar/<int:file_id>', eliminar_archivo, name='eliminar_archivo'),
    path('eliminar_carpeta/<int:folder_id>', eliminar_carpeta, name='eliminar_carpeta'),
    path('mover/<int:file_id>', mover_archivo, name='mover_archivo'),
    path('mover_carpeta/<int:folder_id>', mover_carpeta, name='mover_carpeta'),
]