from django.urls import path
from .views import crear_solicitud_cateqista

urlpatterns = [
    path('crear/', crear_solicitud_cateqista, name='crear_solicitud_catequista'),

]
