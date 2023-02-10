
import pickle
import os.path
from apiclient import errors
import email
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def search_message(service, user_id, search_string):
   
    try:
        list_ids = []
        search_ids = service.users().messages().list(userId=user_id).execute()
        try:
            ids = search_ids['messages']

        except KeyError:
            print("WARNING: the search queried returned 0 results")
            return ""

        if len(ids)>1:
            for msg_id in ids:
                list_ids.append(msg_id['id'])
            return(list_ids)

        else:
            yerp = ids[0]
            print(yerp['id'])
            list_ids.append(yerp['id'])
            return list_ids
        
    except (errors.HttpError):
        print("An error occured: :)") 


def get_message(service, user_id, msg_id):
   
    try:
       ## print("before message dec")     
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_bytes(msg_str)
        ##print('made')
        content_type = mime_msg.get_content_maintype()
        if content_type == 'multipart':
            parts = mime_msg.get_payload()
            final_content = parts[0].get_payload()
            return final_content

        elif content_type == 'text':
            return mime_msg.get_payload()

        else:
            print("\nMessage is not text or multipart, returned an empty string")
            return ""
            
    except Exception:
        print("An error occured: ")


def get_service():
  
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)


    service = build('gmail', 'v1', credentials=creds)

    return service

service = get_service()
user_id= "me"
search_string = ''
msg_id = search_message(service, user_id, search_string)
print("message id: %s" % msg_id)
print("user id: %s" % user_id)
count = 0
messages = []
for i in msg_id:
    messages.append(get_message(service, user_id, msg_id[count]))
    count = count+1
print(count)
print(messages)
unq_msg = 0
dupe = 0
msg_unique = set()
msg_dupe = []
print("Number of emails: " , len(messages))
for msg in messages:
    if msg in msg_unique:
        msg_dupe.append(msg)
        dupe = dupe +1
        
    else:
        msg_unique.add(msg)
        unq_msg = unq_msg +1

print("Number of unique messages: ", len(msg_unique))
print("Number of dumpliate messages: ", len(msg_dupe))

for msg in msg_unique:
    print(msg)

