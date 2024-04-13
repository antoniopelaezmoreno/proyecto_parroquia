from email.mime.text import MIMEText
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]


def enviar_email(sender, to, subject, message_text, user):
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.

  if user.token_json:
    creds = Credentials.from_authorized_user_info(json.loads(user.token_json), SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES,
          redirect_uri="urn:ietf:wg:oauth:2.0:oob"
      )
      creds = flow.run_local_server(port=8081, login_hint=user.email, prompt='consent', access_type='offline')
    # Save the credentials for the next run
    user.token_json =creds.to_json()
    user.save()

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
  
