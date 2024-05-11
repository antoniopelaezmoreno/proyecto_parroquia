from django.urls import path
from .views import index, c403, c404, error, terminar_curso, panel_ciclos

urlpatterns = [
    path('', index, name='index'),
    path('403', c403, name='c403'),
    path('404', c404, name='c404'),
    path('error', error, name='error'),
    path('terminar_curso', terminar_curso, name='terminar_curso'),
    path('panel_ciclos', panel_ciclos, name='panel_ciclos'),


]