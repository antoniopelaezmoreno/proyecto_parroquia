from django.urls import path
from .views import crear_solicitud_cateqista, asignar_catequistas, eliminar_solicitud

urlpatterns = [
    path('crear/', crear_solicitud_cateqista, name='crear_solicitud_catequista'),
    path('asignar_catequistas/', asignar_catequistas, name='asignar_catequistas'),
    path('eliminar_solicitud/<int:solicitud_id>/', eliminar_solicitud, name='eliminar_solicitud'),

]
