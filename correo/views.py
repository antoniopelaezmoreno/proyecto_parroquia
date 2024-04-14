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

def conseguir_credenciales(user):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]

    creds = None

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
            creds = flow.run_local_server(port=8081, login_hint=user.email, prompt='consent', access_type='offline')
            user.token_json = creds.to_json()
            user.save()
    return creds


@login_required
def bandeja_de_entrada(request, query):
    
    creds=conseguir_credenciales(request.user)
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
    creds = conseguir_credenciales(request.user)

    try:
        service = build("gmail", "v1", credentials=creds)
        # Marcar el mensaje como visto
        return service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()

    except HttpError as err:
        from core.views import error
        return error(request, err)
    
@login_required
def obtener_detalles_mensaje(request, mensaje_id):
    # Obtener credenciales del usuario
    creds = conseguir_credenciales(request.user)

    # Construir el servicio de Gmail
    try:
        service = build("gmail", "v1", credentials=creds)

        # Marcar el mensaje como visto
        marcar_mensaje_visto(request, mensaje_id)

        # Obtener detalles del mensaje
        message = service.users().messages().get(userId="me", id=mensaje_id, format='full').execute()
        
        # Extraer los detalles relevantes del mensaje
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        emisor = next((header['value'] for header in headers if header['name'] == 'From'), None)
        if emisor is None:
            emisor = next((header['value'] for header in headers if header['name'] == 'from'),None)
        body = ""
        attachments = []

        # Procesar los partes del mensaje
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/html':  # Tomar solo el primer cuerpo de texto
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'multipart/report' or part['mimeType'] == 'message/delivery-status':
                    receptor = next((header['value'] for header in headers if header['name'] == 'X-Failed-Recipients'), None)
                    body = 'El correo no se ha podido entregar a '+ receptor
                elif 'filename' in part and not part['filename'] == '':
                    attachments.append(part['filename'])

        formatted_date = formatear_fecha(headers)

        # Construir el objeto de respuesta JSON
        response_data = {
            'subject': subject,
            'sender': emisor,
            'body': body,
            'date': formatted_date,
            'attachments': attachments
        }

        # Si es una solicitud POST, procesar el formulario de respuesta
        if request.method == 'POST':
            form_data = request.POST
            destinatario = emisor.split('<')[1].split('>')[0]
            print("destinatario: ", destinatario)
            emisor = request.user.email
            print("emisor: ", emisor)
            asunto = "Re: " + subject
            print("asunto: ", asunto)
            mensaje = form_data.get('mensaje')
            print("mensaje: ", mensaje)
            
            # Llamar al método existente para enviar el correo de respuesta
            try:
                mensaje = create_message(emisor, destinatario, asunto, mensaje)
                send_message(service, "me", mensaje)
                return redirect('bandeja_de_entrada_familias')
            except HttpError as err:
            # Manejar la excepción HttpError
                return JsonResponse({'success': False, 'error': str(err)})

            except Exception as e:  
                # Manejar otras excepciones
                return JsonResponse({'success': False, 'error': str(e)})

        # Si es una solicitud GET, renderizar la página de detalles del mensaje
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
    try:
        user=request.user
        creds = conseguir_credenciales(user)
        service = build("gmail", "v1", credentials=creds)

        if request.method == 'POST':
            sender = request.user.email
            
            destinatarios = request.POST.get('destinatario')
            lista_destinatarios = destinatarios.split(',')  # Dividir las direcciones por comas
            subject = request.POST.get('asunto')
            message_text = request.POST.get('mensaje')

            for destinatario in lista_destinatarios:
                message = create_message(sender, destinatario.strip(), subject, message_text)  # strip() para eliminar espacios en blanco
                send_message(service, "me", message)
            
            # Devolver una respuesta JSON
            return JsonResponse({'success': True})
        
        # En caso de que no sea una solicitud POST
        return JsonResponse({'success': False, 'error': 'No es una solicitud POST'})
    
    except HttpError as err:
        # Manejar la excepción HttpError
        return JsonResponse({'success': False, 'error': str(err)})

    except Exception as e:
        # Manejar otras excepciones
        return JsonResponse({'success': False, 'error': str(e)})
    
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        'raw': raw_message.decode("utf-8")
    }
  
def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None
    
    


