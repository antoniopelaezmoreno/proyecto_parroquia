from django.shortcuts import render, redirect
from django.db.models import Q
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
import base64
from django.contrib.auth.decorators import login_required
from catecumeno.models import Catecumeno
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from custom_user.models import CustomUser
from solicitud_catequista.models import SolicitudCatequista
from email.mime.text import MIMEText
from django.http import JsonResponse, HttpResponseServerError, HttpResponseRedirect
import re
from django.urls import reverse

# Create your views here.

@login_required
def bandeja_salida(request):
    request.session['redirect_to'] = "outbox"
    creds=conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds
    try:
        service = build("gmail", "v1", credentials=creds)
        remitentes = obtener_remitentes_interesados(request)
        query = ' OR '.join([f"to:{remitente}  OR  To:{remitente}" for remitente in remitentes])
        results = service.users().messages().list(userId="me",q=query, labelIds=["SENT"]).execute()
        messages = results.get("messages", [])

        paginator = Paginator(messages, 10)  # 10 mensajes por página
        page = request.GET.get('page')
        try:
            mensajes_pagina = paginator.page(page)
        except PageNotAnInteger:
            mensajes_pagina = paginator.page(1)
        except EmptyPage:
            mensajes_pagina = paginator.page(paginator.num_pages)

        mensajes = []
        for message in mensajes_pagina:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'subject'), None)
            if subject is None:
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            
            body = msg['snippet']
            if subject == "":
                subject = "(sin asunto)"
            if body == "":
                body = "(sin contenido)"
            receptor = next((header['value'] for header in headers if header['name'] == 'to'), None)
            if receptor is None:
                receptor = next((header['value'] for header in headers if header['name'] == 'To'), None)

            fecha = formatear_fecha(headers)

            mensajes.append({'subject': subject, 'body': body, 'receiver': receptor, 'date': fecha, 'id': message['id']})

        return render(request, 'bandeja_salida.html', {'mensajes_pagina': mensajes_pagina, 'mensajes': mensajes})
    except HttpError as err:
        from core.views import error
        return error(request, err)

@login_required
def obtener_remitentes_interesados(request):
    correos_solicitudes=[]
    if request.user.is_superuser:
        query = Q()
        query |= Q(email__isnull=False)
        query |= Q(email_madre__isnull=False)
        query |= Q(email_padre__isnull=False)
        familias = Catecumeno.objects.filter(query).values_list('email', 'email_madre', 'email_padre')
        correos_solicitudes = list(SolicitudCatequista.objects.all().values_list('email', flat=True))
    elif request.user.is_coord:
        query = Q()
        query |= Q(email__isnull=False)
        query |= Q(email_madre__isnull=False)
        query |= Q(email_padre__isnull=False)
        familias = Catecumeno.objects.filter(query, ciclo=request.user.ciclo).values_list('email', 'email_madre', 'email_padre')
    else:
        familias=[]
    
    
    familias = [email for tupla in familias for email in tupla if email]
    familias.append("mailer-daemon@googlemail.com")

    catequistas = list(CustomUser.objects.all().values_list('email', flat=True))
    remitentes = familias + catequistas + correos_solicitudes

    return remitentes

def conseguir_credenciales(request, user):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", 
              "https://www.googleapis.com/auth/gmail.send", 
              "https://www.googleapis.com/auth/gmail.modify", 
              "https://www.googleapis.com/auth/calendar"]

    creds = None

    try:
        if user.token_json:
            creds = Credentials.from_authorized_user_info(json.loads(user.token_json), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("estoy dentro")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))
                authorization_url, state = flow.authorization_url(
                    access_type='offline', 
                    login_hint=user.email, 
                    prompt='consent'
                )
                request.session['state'] = state
                print("despues de la autorizacion")
                return HttpResponseRedirect(authorization_url)

    except OSError as e:
        return HttpResponseServerError("Error: Ha habido un error. Por favor, inténtalo de nuevo más tarde.")
    return creds

def oauth2callback(request):
    # Especificar el estado al crear el flujo en la devolución de llamada para que pueda
    # ser verificado en la respuesta del servidor de autorización.
    print("En oauth2callback")
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", 
              "https://www.googleapis.com/auth/gmail.send", 
              "https://www.googleapis.com/auth/gmail.modify", 
              "https://www.googleapis.com/auth/calendar"]
    state = request.session.pop('state', "")
    flow = Flow.from_client_secrets_file(
        "credentials.json", scopes=SCOPES, state=state)
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    # Utilizar la respuesta del servidor de autorización para obtener los tokens OAuth 2.0.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Almacenar las credenciales en la sesión del usuario
    credentials = flow.credentials
    print("Credenciales: ", credentials)
    creds = credentials.to_json()
    request.user.token_json = creds
    request.user.save()

    redirect_to = request.session.get('redirect_to', 'index')
    del request.session['redirect_to']

    return redirect(redirect_to)

@login_required
def bandeja_de_entrada(request):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", 
              "https://www.googleapis.com/auth/gmail.send", 
              "https://www.googleapis.com/auth/gmail.modify", 
              "https://www.googleapis.com/auth/calendar"]
    
    request.session['redirect_to'] = "inbox"

    creds=conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds
    print("Ya he salido")
    try:
        service = build("gmail", "v1", credentials=creds)
        remitentes = obtener_remitentes_interesados(request)
        query = ' OR '.join([f"from:{remitente}" for remitente in remitentes])
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
            if subject is None:
                subject = next((header['value'] for header in headers if header['name'] == 'subject'), None)
            emisor = next((header['value'] for header in headers if header['name'] == 'From'), None)
            if emisor is None:
                emisor = next((header['value'] for header in headers if header['name'] == 'from'),None)
            body = msg['snippet']

            if subject == "":
                subject = "(sin asunto)"
            if body == "":
                body = "(sin contenido)"

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
    creds = conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds

    try:
        service = build("gmail", "v1", credentials=creds)
        # Marcar el mensaje como visto
        return service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()

    except HttpError as err:
        from core.views import error
        return error(request, err)
    
@login_required
def obtener_detalles_mensaje(request, mensaje_id):
    creds = conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds

    try:
        service = build("gmail", "v1", credentials=creds)

        marcar_mensaje_visto(request, mensaje_id)

        message = service.users().messages().get(userId="me", id=mensaje_id, format='full').execute()
        
        # Extraer los detalles relevantes del mensaje
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        if subject is None:
                subject = next((header['value'] for header in headers if header['name'] == 'subject'), None)
        emisor = next((header['value'] for header in headers if header['name'] == 'From'), None)
        if emisor is None:
            emisor = next((header['value'] for header in headers if header['name'] == 'from'),None)
        body = ""
        attachments = []

        # Procesar los partes del mensaje
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                # Si es multipart/alternative, buscar el cuerpo en texto plano o HTML
                if part['mimeType'] == 'multipart/alternative':
                    for subpart in part['parts']:
                        if subpart['mimeType'] == 'text/html':
                            # Decodificar y agregar el cuerpo HTML
                            body += base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                # Si es una parte independiente de texto/html, agregarla
                elif part['mimeType'] == 'text/html':
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                # Si tiene nombre de archivo, agregarlo a los archivos adjuntos
                elif 'filename' in part and part['filename']:
                    attachments.append(part['filename'])
        else:
            if 'payload' in message:
                payload = message['payload']
                if 'body' in payload:
                    # Si hay un cuerpo directo, usarlo
                    body_data = payload['body']['data']
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                elif 'parts' in payload:
                    # Si hay partes en el payload, procesarlas
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/html':
                            # Si es texto plano, agregar al cuerpo
                            body_data = part['body']['data']
                            body += base64.urlsafe_b64decode(body_data).decode('utf-8')

        formatted_date = formatear_fecha(headers)

        # Construir el objeto de respuesta JSON
        response_data = {
            'subject': subject,
            'sender': emisor,
            'body': body,
            'date': formatted_date,
            'attachments': attachments
        }
        print(emisor)

        # Si es una solicitud POST, procesar el formulario de respuesta
        if request.method == 'POST':
            form_data = request.POST
            if "<" in emisor:
                destinatario = emisor.split('<')[1].split('>')[0]
            else:
                destinatario = emisor
            emisor = request.user.email
            asunto = "Re: " + subject
            mensaje = form_data.get('mensaje')
                
            # Llamar al método existente para enviar el correo de respuesta
            try:
                mensaje = create_message(emisor, destinatario, asunto, mensaje)
                send_message(service, "me", mensaje)
                return redirect('inbox')
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
    
@login_required
def obtener_detalles_mensaje_enviado(request, mensaje_id):
    creds = conseguir_credenciales(request, request.user)
    if isinstance(creds, HttpResponseRedirect):
        return creds

    try:
        service = build("gmail", "v1", credentials=creds)

        marcar_mensaje_visto(request, mensaje_id)

        message = service.users().messages().get(userId="me", id=mensaje_id, format='full').execute()
        
        # Extraer los detalles relevantes del mensaje
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        if subject is None:
                subject = next((header['value'] for header in headers if header['name'] == 'subject'), None)
        receptor = next((header['value'] for header in headers if header['name'] == 'to'), None)
        if receptor is None:
            receptor = next((header['value'] for header in headers if header['name'] == 'To'),None)
        body = ""
        attachments = []

        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                # Si es multipart/alternative, buscar el cuerpo en texto plano o HTML
                if part['mimeType'] == 'multipart/alternative':
                    for subpart in part['parts']:
                        if subpart['mimeType'] == 'text/html':
                            # Decodificar y agregar el cuerpo HTML
                            body += base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                # Si es una parte independiente de texto/html, agregarla
                elif part['mimeType'] == 'text/html':
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                # Si tiene nombre de archivo, agregarlo a los archivos adjuntos
                elif 'filename' in part and part['filename']:
                    attachments.append(part['filename'])
        else:
            if 'payload' in message:
                payload = message['payload']
                if 'body' in payload:
                    # Si hay un cuerpo directo, usarlo
                    body_data = payload['body']['data']
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                elif 'parts' in payload:
                    # Si hay partes en el payload, procesarlas
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/html':
                            # Si es texto plano, agregar al cuerpo
                            body_data = part['body']['data']
                            body += base64.urlsafe_b64decode(body_data).decode('utf-8')
            
        formatted_date = formatear_fecha(headers)

        # Construir el objeto de respuesta JSON
        response_data = {
            'subject': subject,
            'receiver': receptor,
            'body': body,
            'date': formatted_date,
            'attachments': attachments
        }

        return render(request, 'detalles_mensaje_enviado.html', {'mensaje': response_data})

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
        creds = conseguir_credenciales(request, user)
        if isinstance(creds, HttpResponseRedirect):
            return creds
        service = build("gmail", "v1", credentials=creds)

        if request.method == 'POST':
            sender = request.user.email
            
            destinatarios = request.POST.get('destinatario')
            if destinatarios == "":
                return JsonResponse({'success': False, 'error': 'No se ha especificado ningún destinatario'})
            lista_destinatarios = [email.strip() for email in destinatarios.split(',') if re.match(r'^[\w\.-]+@[\w\.-]+(?:\.[\w]+)+$', email.strip())]
            
            if not lista_destinatarios:
                return JsonResponse({'success': False, 'error': 'Las direcciones de correo electrónico no son válidas'})
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
    
    


