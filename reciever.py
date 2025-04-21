import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the required Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def authenticate_gmail_api():
    """Authenticate with Google API and return service"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages_from_sender(service, sender_email, label_ids=[]):
    """Get the latest messages from a specific sender"""
    query = f"from:{sender_email}"
    results = service.users().messages().list(userId='me', labelIds=label_ids, q=query).execute()
    messages = results.get('messages', [])
    if not messages:
        print('No messages found.')
        return None
    else:
        # Fetch the latest message (first message in the list)
        latest_message = messages[0]
        msg = service.users().messages().get(userId='me', id=latest_message['id']).execute()
        return msg

def get_message_details(message):
    """Print details of the message, including the body"""
    payload = message['payload']
    headers = payload['headers']
    
    # Find and print the subject and sender from the message headers
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'From':
            sender = header['value']
    
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    
    # Decode the body of the email (if plain text)
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    print(f"Body: {body[:500]}...")  # Print the first 500 characters of the body

def main():
    sender_email = "sender@domain.tld"
    service = authenticate_gmail_api()
    latest_message = list_messages_from_sender(service, sender_email)
    
    if latest_message:
        get_message_details(latest_message)

if __name__ == '__main__':
    main()
