from django.shortcuts import render
from django.db.models import Q
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from django.contrib.auth.decorators import login_required
from catecumeno.models import Catecumeno
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from custom_user.models import CustomUser

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
    query = ' OR '.join([f"from:{remitente}" for remitente in remitentes])

    return bandeja_de_entrada(request, query)

@login_required
def bandeja_entrada_catequistas(request):
    catequistas = CustomUser.objects.all().values_list('email', flat=True)
    query = ' OR '.join([f"from:{catequista}" for catequista in catequistas])
    return bandeja_de_entrada(request, query)


@login_required
def bandeja_de_entrada(request, query):
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
            body = msg['snippet']

            # Recibimos y transformamos la fecha al formato dd/mm/YYYY
            fecha = next((header['value'] for header in headers if header['name'] == 'Date'), None)
            fecha_sin_utc = fecha.split(" (")[0]
            fecha_recibido = datetime.strptime(fecha_sin_utc, '%a, %d %b %Y %H:%M:%S %z')
            fecha_formateada = fecha_recibido.strftime('%d/%m/%Y')
        
            if 'UNREAD' in msg['labelIds']:
                leido = False
            else:
                leido = True
            mensajes.append({'subject': subject, 'body': body, 'sender': emisor, 'seen': leido, 'date': fecha_formateada})

        return render(request, 'bandeja_de_entrada.html', {'mensajes_pagina': mensajes_pagina, 'mensajes': mensajes})
    except HttpError as err:
        from core.views import error
        return error(request, err)
    


