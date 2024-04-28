"""
URL configuration for proyecto_parroquia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler500

handler500 = 'core.views.c500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('user/', include('custom_user.urls')),
    path('catecumeno/', include('catecumeno.urls')),
    path('catequista/', include('solicitud_catequista.urls')),
    path('auth/', include('allauth.urls')),
    path('curso/', include('curso.urls')),
    path('grupo/', include('grupo.urls')),
    path('sesion/', include('sesion.urls')),
    path('drive/', include('drive.urls')),
    path('notificacion/', include('notificacion.urls')),
    path('sala/', include('sala.urls')),
    path('correo/', include('correo.urls')),
    path('evento/', include('evento.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
