import os.path
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from users import RECIPIENTS  # Replace with your list of recipients

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()

# ==== USAGE EXAMPLE ====
if __name__ == '__main__':
    service = gmail_authenticate()

    for recipient in RECIPIENTS:
        message = f"""Hi {recipient},

This is a sample email sent using the Gmail API.
You can customize this message content however you like.

Regards,
Your Name"""

        msg = create_message(
            sender='youremail@example.com',
            to=f'{recipient}@example.com',
            subject='Example Subject Line',
            message_text=message
        )

        result = send_email(service, 'me', msg)
        print(f"Email sent! Message ID: {result['id']}")
