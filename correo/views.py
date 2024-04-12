from django.shortcuts import render, redirect
from django.db.models import Q
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import base64
from django.contrib.auth.decorators import login_required
from catecumeno.models import Catecumeno
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from custom_user.models import CustomUser
from email.mime.text import MIMEText
from django.http import JsonResponse

# Create your views here.
@login_required
def bandeja_entrada_familias(request):
    if request.user.is_superuser:
        query = Q()
        query |= Q(email__isnull=False)
        query |= Q(email_madre__isnull=False)
        query |= Q(email_padre__isnull=False)
        remitentes = Catecumeno.objects.filter(query).values_list('email', 'email_madre', 'email_padre')
    elif request.user.is_coord:
        query = Q()
        query |= Q(email__isnull=False)
        query |= Q(email_madre__isnull=False)
        query |= Q(email_padre__isnull=False)
        remitentes = Catecumeno.objects.filter(query, ciclo=request.user.ciclo).values_list('email', 'email_madre', 'email_padre')
    else:
        remitentes=[]
    

    remitentes = [email for tupla in remitentes for email in tupla if email]
    remitentes.append("mailer-daemon@googlemail.com")
    query = ' OR '.join([f"from:{remitente}" for remitente in remitentes])

    return bandeja_de_entrada(request, query)

@login_required
def bandeja_entrada_catequistas(request):
    catequistas = list(CustomUser.objects.all().values_list('email', flat=True))
    catequistas.append("mailer-daemon@googlemail.com")
    query = ' OR '.join([f"from:{catequista}" for catequista in catequistas])
    return bandeja_de_entrada(request, query)

def conseguir_credenciales(request):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

    creds = None
    user = request.user

    if user.token_json:
        creds = Credentials.from_authorized_user_info(json.loads(user.token_json), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            creds = flow.run_local_server(port=8081, login_hint=user.email)
            user.token_json = creds.to_json()
            user.save()
    return creds


@login_required
def bandeja_de_entrada(request, query):
    
    creds=conseguir_credenciales(request)
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me",q=query, labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        # Crear un paginador con los mensajes
        paginator = Paginator(messages, 10)  # 10 mensajes por página

        # Obtener el número de página solicitado (por defecto, página 1)
        page = request.GET.get('page')
        try:
            mensajes_pagina = paginator.page(page)
        except PageNotAnInteger:
            # Si el número de página no es un entero, mostrar la primera página
            mensajes_pagina = paginator.page(1)
        except EmptyPage:
            # Si la página está fuera de rango (por ejemplo, 9999), mostrar la última página
            mensajes_pagina = paginator.page(paginator.num_pages)

        mensajes = []
        for message in mensajes_pagina:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            emisor = next((header['value'] for header in headers if header['name'] == 'From'), None)
            if emisor is None:
                emisor = next((header['value'] for header in headers if header['name'] == 'from'),None)
            body = msg['snippet']

            fecha=formatear_fecha(headers)
            
            if 'UNREAD' in msg['labelIds']:
                leido = False
            else:
                leido = True
            mensajes.append({'subject': subject, 'body': body, 'sender': emisor, 'seen': leido, 'date': fecha, 'id': message['id']})

        return render(request, 'bandeja_de_entrada.html', {'mensajes_pagina': mensajes_pagina, 'mensajes': mensajes})
    except HttpError as err:
        from core.views import error
        return error(request, err)
    
@login_required
def marcar_mensaje_visto(request, message_id):
    creds = conseguir_credenciales(request)

    try:
        service = build("gmail", "v1", credentials=creds)
        # Marcar el mensaje como visto
        service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()

        # Devolver una respuesta JSON
        return JsonResponse({'success': True})

    except HttpError as err:
        from core.views import error
        return error(request, err)
    
@login_required
def obtener_detalles_mensaje(request, mensaje_id):
    # Obtener credenciales del usuario
    creds = conseguir_credenciales(request)

    # Construir el servicio de Gmail
    try:
        service = build("gmail", "v1", credentials=creds)

        # Obtener detalles del mensaje
        message = service.users().messages().get(userId="me", id=mensaje_id, format='full').execute()

        # Extraer los detalles relevantes del mensaje
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        emisor = next((header['value'] for header in headers if header['name'] == 'From'), None)
        if emisor is None:
            emisor = next((header['value'] for header in headers if header['name'] == 'from'),None)
        body = message['snippet']
        formatted_date = formatear_fecha(headers)

        # Verificar si el mensaje tiene archivos adjuntos
        attachments = []
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if 'filename' in part:
                    attachments.append(part['filename'])

        # Construir el objeto de respuesta JSON
        response_data = {
            'subject': subject,
            'sender': emisor,
            'body': body,
            'date': formatted_date,
            'attachments': attachments
        }

        return render(request, 'detalles_mensaje.html', {'mensaje': response_data})

    except Exception as err:
        from core.views import error
        return error(request, err)

def formatear_fecha(headers):
    fecha = next((header['value'] for header in headers if header['name'] == 'Date'), None)
    if "+" in fecha:
        fecha_sin_utc = fecha.split(" +")[0]
    elif "-" in fecha:
        fecha_sin_utc = fecha.split(" -")[0]
    fecha_recibido = datetime.strptime(fecha_sin_utc, '%a, %d %b %Y %H:%M:%S')
    fecha_formateada = fecha_recibido.strftime('%d/%m/%Y')
    return fecha_formateada

@login_required
def enviar_correo(request):
    creds = conseguir_credenciales(request)

    try:
        service = build("gmail", "v1", credentials=creds)
        if request.method == 'POST':
            sender = request.user.email
            to = request.POST.get('destinatario')
            subject = request.POST.get('asunto')
            message_text = request.POST.get('mensaje')

            message = create_message(sender, to, subject, message_text)
            send_message(service, "me", message)
            
            # Devolver una respuesta JSON
            return JsonResponse({'success': True})
        
        # En caso de que no sea una solicitud POST
        return JsonResponse({'success': False, 'error': 'No es una solicitud POST'})
    
    except HttpError as err:
        from core.views import error
        return error(request, err)
    
@login_required
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        'raw': raw_message.decode("utf-8")
    }
  
@login_required
def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None
    
    


