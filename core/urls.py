from django.urls import path
from .views import index, c403, c404

urlpatterns = [
    path('', index, name='index'),
    path('403', c403, name='c403'),
    path('404', c404, name='c404'),


]