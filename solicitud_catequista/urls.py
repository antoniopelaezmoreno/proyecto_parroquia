from django.urls import path
from .views import crear_solicitud_cateqista, asignar_catequistas

urlpatterns = [
    path('crear/', crear_solicitud_cateqista, name='crear_solicitud_catequista'),
    path('asignar_catequistas/', asignar_catequistas, name='asignar_catequistas'),

]
