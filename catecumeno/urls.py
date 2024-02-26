from django.urls import path
from .views import crear_catecumeno, listar_catecumenos

urlpatterns = [
    path('crear/', crear_catecumeno, name='crear_catecumeno'),
    path('listar/', listar_catecumenos, name='listar_catecumenos')
]
