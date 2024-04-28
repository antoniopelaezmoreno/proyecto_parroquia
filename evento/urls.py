from django.urls import path
from .views import crear_evento, nuevo_evento, obtener_eventos,mostrar_eventos, detalles_evento

urlpatterns = [
    path('crear/', crear_evento, name='crear_evento'),
    path('nuevo/', nuevo_evento, name='nuevo_evento'),
    path('obtener_eventos/', obtener_eventos, name='obtener_eventos'),
    path('listar/', mostrar_eventos, name='mostrar_eventos'),
    path('<int:evento_id>/', detalles_evento, name='detalles_evento'),

]