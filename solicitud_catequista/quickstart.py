from email.mime.text import MIMEText
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from correo.views import conseguir_credenciales
import base64
import json

# If modifying these scopes, delete the file token.json.

def enviar_email(request, sender, to, subject, message_text, user):
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  request.session['redirect_to'] = request.path
  creds = conseguir_credenciales(request, user)

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    message = create_message(sender, to, subject, message_text)
    send_message(service, "me", message)

    

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }

def create_draft(service, user_id, message_body):
  try:
    message = {'message': message_body}
    draft = service.users().drafts().create(userId=user_id, body=message).execute()
    return draft
  except Exception as e:
    print('An error occurred: %s' % e)
    return None
  
def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None
  
