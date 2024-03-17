from django.urls import path
from .views import subir_archivo, listar_archivos, crear_carpeta


urlpatterns = [
    path('subir', subir_archivo, name='subir_archivo'),
    path('subir/<int:folder_id>', subir_archivo, name='subir_archivo_en_carpeta'),
    path('listar', listar_archivos, name='listar_archivos'),
    path('listar/<int:folder_id>', listar_archivos, name='listar_archivos_en_carpeta'),
    path('crear_carpeta', crear_carpeta, name='crear_carpeta'),
    path('crear_carpeta/<int:folder_id>', crear_carpeta, name='crear_carpeta_en_carpeta'),


]