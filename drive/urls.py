from django.urls import path
from .views import subir_archivo, listar_archivos


urlpatterns = [
    path('subir', subir_archivo, name='subir_archivo'),
    path('listar', listar_archivos, name='listar_archivos')


]