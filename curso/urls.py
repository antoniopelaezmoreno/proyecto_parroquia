from django.urls import path
from .views import crear_curso

urlpatterns = [
    path('crear/', crear_curso, name='crear_curso')
]