from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sala, Reserva
from custom_user.models import CustomUser
from datetime import timedelta, date
from django.http import HttpResponse

@login_required
def obtener_salas_disponibles(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        salas_disponibles = Sala.objects.exclude(
            reserva__fecha=fecha,
            reserva__hora_inicio__lt=hora_fin,
            reserva__hora_fin__gt=hora_inicio
        )
        print(salas_disponibles)
        return render(request, 'salas_disponibles.html', {'salas_disponibles': salas_disponibles})

    return render(request, 'salas_disponibles.html')



@login_required
def crear_reservas_por_defecto(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        sala_id = request.POST.get('sala')
        dia_semana = int(request.POST.get('dia_semana'))
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        # Obtener usuario y sala
        usuario = CustomUser.objects.get(pk=usuario_id)
        sala = Sala.objects.get(pk=sala_id)
        
        # Obtener la fecha actual
        fecha_actual = date.today()

        # Calcular la fecha del próximo día de la semana elegido
        dia_actual = fecha_actual.weekday()
        dias_para_dia_elegido = (dia_semana - dia_actual + 7) % 7
        proxima_fecha = fecha_actual + timedelta(days=dias_para_dia_elegido)

        # Calcular la fecha límite (30 de junio)
        fecha_limite = date(fecha_actual.year, 6, 30)

        # Crear reservas hasta la fecha límite (30 de junio) para cada viernes
        while proxima_fecha <= fecha_limite:
            reserva = Reserva.objects.create(usuario=usuario, sala=sala, fecha=proxima_fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
            proxima_fecha += timedelta(weeks=1)
        
        return HttpResponse('Reservas creadas exitosamente.')  # O redirigir a una página de éxito

    salas = Sala.objects.all()
    usuarios = CustomUser.objects.filter(is_coord=True)
    return render(request, 'crear_reservas.html', {'salas': salas, 'usuarios': usuarios})
