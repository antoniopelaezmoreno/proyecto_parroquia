from django.urls import path
from .views import index, c403, c404, error, terminar_curso, panel_ciclos, panel_ultimas_ausencias, notificar_familias_ultima_ausencia, panel_ausencias_reiteradas, notificar_familias_ausencias_reiteradas, pantalla_confirmacion_exito

urlpatterns = [
    path('', index, name='index'),
    path('403', c403, name='c403'),
    path('404', c404, name='c404'),
    path('error', error, name='error'),
    path('terminar_curso', terminar_curso, name='terminar_curso'),
    path('panel_ciclos', panel_ciclos, name='panel_ciclos'),
    path('panel_ultimas_ausencias', panel_ultimas_ausencias, name='panel_ultimas_ausencias'),
    path('notificar_familias_ultima_ausencia/<int:catecumeno_id>', notificar_familias_ultima_ausencia, name='notificar_familias_ultima_ausencia'),
    path('panel_ausencias_reiteradas', panel_ausencias_reiteradas, name='panel_ausencias_reiteradas'),
    path('notificar_familias_ausencias_reiteradas/<int:catecumeno_id>', notificar_familias_ausencias_reiteradas, name='notificar_familias_ausencias_reiteradas'),
    path('pantalla_confirmacion_exito', pantalla_confirmacion_exito, name='pantalla_confirmacion_exito'),


]