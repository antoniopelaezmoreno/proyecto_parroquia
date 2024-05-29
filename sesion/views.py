from django.shortcuts import render, redirect, get_object_or_404
from .forms import SesionForm
from .models import Catecumeno
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sesion
from grupo.models import Grupo
from curso.models import Curso
from custom_user.models import CustomUser
from evento.views import asociar_a_google_calendar
from django.db.models import Count
from correo.views import conseguir_credenciales
from googleapiclient.discovery import build
from django.http import HttpResponseRedirect
# Create your views here.

@login_required
def crear_sesion(request):
    if request.user.is_authenticated:
        
        request.session['redirect_to'] = request.path
        creds= conseguir_credenciales(request, request.user)
        if isinstance(creds, HttpResponseRedirect):
            return creds
        ciclo=request.user.ciclo
        if request.user.is_superuser:
            ciclo = request.POST.get('ciclo')
        
        if request.method == 'POST':
            form = SesionForm(request.POST, request.FILES)
            if form.is_valid():
                fecha = form.cleaned_data['fecha']
                if fecha >= timezone.now().date():
                    sesion = form.save(commit=False)
                    sesion.ciclo = ciclo

                    if ciclo == 'posco_1' or ciclo == 'posco_2' or ciclo == 'gr_juv_1' or ciclo == 'gr_juv_2':
                        sesion.hora_inicio = '16:30'
                        sesion.hora_fin = '17:30'
                    elif ciclo == 'posco_3' or ciclo == 'posco_4':
                        sesion.hora_inicio = '17:30'
                        sesion.hora_fin = '18:30'
                    elif ciclo == 'catecumenados_3':
                        sesion.hora_inicio = '19:00'
                        sesion.hora_fin = '20:30'
                    else:
                        sesion.hora_inicio = '17:00'
                        sesion.hora_fin = '18:30'


                    sesion.save()

                    files = form.cleaned_data['files']
                    for file in files:
                        sesion.files.add(file)
                    
                    crear_sesion_en_calendar(request,sesion, request.user)
                    return redirect('/sesion/listar')
                else:
                    messages.error(request, "La fecha no puede estar en el pasado")
            else:
                messages.error(request, "Hay algo mal en el formulario, por favor revisa los campos")
        else:
            form = SesionForm()
        return render(request, 'crear_sesion.html', {'form': form})
    else:
        return redirect('/403')
    

@login_required
def crear_sesion_en_calendar(request,sesion, user):

    creds = conseguir_credenciales(request, user)
    if isinstance(creds, HttpResponseRedirect):
        return creds
    catequistas = CustomUser.objects.filter(ciclo = user.ciclo)
    
    event={
        'summary': sesion.titulo,
        'description': sesion.descripcion,
        'start': {
            'dateTime': str(sesion.fecha) + 'T' + str(sesion.hora_inicio) + ':00',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': str(sesion.fecha) + 'T' + str(sesion.hora_fin) + ':00',
            'timeZone': 'UTC',
        }
    }
    if catequistas:
        event['attendees']=[{'email': usuario.email} for usuario in catequistas]
    
    try:
        service = build("calendar", "v3", credentials=creds)
        event=service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print('Error creating event: %s' % (e))

@login_required
def editar_sesion(request, sesionId):
    sesion = get_object_or_404(Sesion, pk=sesionId)
    if request.user.ciclo == sesion.ciclo or request.user.is_superuser:
        if request.method == 'POST':
            form = SesionForm(request.POST, request.FILES, instance=sesion)
            if form.is_valid():
                sesion = form.save(commit=False)
                sesion.save()
                sesion.files.clear()
                files = form.cleaned_data['files']
                for file in files:
                    sesion.files.add(file)
                return redirect('/sesion/listar')
            else:
                messages.error(request, "Hay algo mal en el formulario, por favor revisa los campos")
        else:
            form = SesionForm(instance=sesion)
        return render(request, 'editar_sesion.html', {'form': form, 'sesion': sesion})
    else:
        return redirect('/403')

    

@login_required
def eliminar_sesion(request, sesionId):
    sesion = get_object_or_404(Sesion, pk=sesionId)
    if request.user.ciclo == sesion.ciclo or request.user.is_superuser:
        sesion.delete()
        return redirect('/sesion/listar')
    else:
        return redirect('/403')
 
@login_required
def listar_sesiones(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            sesiones = Sesion.objects.all().order_by('fecha', 'id')
            return render(request, 'listar_sesiones_admin.html', {'sesiones': sesiones})
        else:
            ciclo=request.user.ciclo
            sesiones = Sesion.objects.filter(ciclo=ciclo).order_by('fecha', 'id')
            return render(request, 'listar_sesiones.html', {'sesiones': sesiones})
    else:
        return redirect('/403')


@login_required
def pasar_lista(request, sesionid):
    from core.views import error
    if request.user.is_authenticated:
        sesion = get_object_or_404(Sesion, pk=sesionid)
        if request.user.ciclo == sesion.ciclo:
            if sesion.fecha > timezone.now().date():
                return error(request, "No puedes pasar lista de una sesión futura")
            if request.method == 'POST':
                print("dentro de post")
                sesion.asistentes.clear()
                sesion.justificados.clear()
                sesion.ausentes.clear()
                for catecumeno in catecumenos_desde_catequista(request.user):
                    categoria = request.POST.get(f'categoria_{catecumeno.id}')
                    if categoria in ['asistente', 'justificado', 'ausente']:
                        if categoria == 'asistente':
                            print("asistente")
                            sesion.asistentes.add(catecumeno)
                        elif categoria == 'justificado':
                            print("justificado")
                            sesion.justificados.add(catecumeno)
                            print(sesion.justificados.all())
                        elif categoria == 'ausente':
                            print("ausente")
                            sesion.ausentes.add(catecumeno)
                    else:
                        return error(request, "Categoría no válida")
                sesion.save()
                print("despues de guardar")
                return redirect('/sesion/listar')
            else:
                catecumenos = catecumenos_desde_catequista(request.user)
                return render(request, 'pasar_lista.html', {'sesion': sesion, 'catecumenos': catecumenos})
        else:
            return redirect('/403')
    else:
        return redirect('/403')

def catecumenos_desde_catequista(catequista):
    grupo1 = Grupo.objects.filter(catequista1=catequista).first()
    grupo2 = Grupo.objects.filter(catequista2=catequista).first()
    
    if grupo1:
        return grupo1.miembros()
    elif grupo2:
        return grupo2.miembros()
    else:
        return []
@login_required
def tabla_asistencias_grupo(request):
    if not request.user.is_authenticated:
        return redirect('/403')
    catecumenos = catecumenos_desde_catequista(request.user)
    sesiones = Sesion.objects.filter(ciclo=request.user.ciclo, curso = Curso.objects.latest('id')).order_by('fecha')
    return render(request, 'tabla_asistencias.html', {'catecumenos': catecumenos, 'sesiones': sesiones})

@login_required
def tabla_asitencias_coord(request):
    if not request.user.is_authenticated:
        return redirect('/403')
    
    if request.user.is_coord:
        grupos = Grupo.objects.filter(ciclo=request.user.ciclo)
        sesiones = Sesion.objects.filter(ciclo=request.user.ciclo, curso=Curso.objects.latest('id')).order_by('fecha')
        return render(request, 'tabla_asistencias_coord.html', {'grupos': grupos, 'sesiones': sesiones})
    elif request.user.is_superuser:
        redirect('/sesion/tabla_asistencia_admin/posco_1')

@login_required
def tabla_asistencias_admin(request, ciclo):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/403')
    elif ciclo not in [choice[0] for choice in Catecumeno.CicloChoices.choices]:
        return redirect('/404')
    else:
        grupos = Grupo.objects.filter(ciclo=ciclo)
        sesiones = Sesion.objects.filter(ciclo=ciclo, curso=Curso.objects.latest('id')).order_by('fecha')
        return render(request, 'tabla_asistencias_admin.html', {'sesiones': sesiones, 'grupos': grupos})
    
@login_required
def contar_ausencias(request):
    if request.user.is_superuser:
        return redirect('/403')
    sesiones_ausentes = Sesion.objects.filter(ciclo = request.user.ciclo, ausentes__isnull=False)
    if request.user.is_coord:
        catecumenos_con_ausencias = Catecumeno.objects.annotate(num_ausencias=Count('sesiones_ausentes')).filter(num_ausencias__gte=3)

        return catecumenos_con_ausencias
    else:
        catecumenos = catecumenos_desde_catequista(request.user)
        catecumenos_con_ausencias = Catecumeno.objects.annotate(num_ausencias=Count('sesiones_ausentes')).filter(num_ausencias__gte=3).filter(id__in=[catecumeno.id for catecumeno in catecumenos])
        return catecumenos_con_ausencias
    
@login_required
def contar_ausencias_ultima_sesion(request):
    if request.user.is_superuser:
        return redirect('/403')
    sesion = Sesion.objects.filter(ciclo=request.user.ciclo, fecha__lte=timezone.now().date())
    
    if sesion.exists():
        sesion = sesion.latest('fecha')
    else:
        return []
    
    if request.user.is_coord:
        return sesion.ausentes.all()
    else:
        catecumenos = catecumenos_desde_catequista(request.user)
        return sesion.ausentes.filter(id__in=[catecumeno.id for catecumeno in catecumenos])