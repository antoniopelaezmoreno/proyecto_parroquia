from django.contrib import admin
from .models import Sala, Reserva, SolicitudReserva
# Register your models here.

admin.site.register(Sala)
admin.site.register(Reserva)
admin.site.register(SolicitudReserva)

