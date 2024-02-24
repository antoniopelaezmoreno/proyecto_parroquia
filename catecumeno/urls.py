from django.urls import path
from .views import crear_catecumeno

urlpatterns = [
    path('crear/', crear_catecumeno, name='crear_catecumeno'),
]
