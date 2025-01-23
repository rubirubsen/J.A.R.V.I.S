from dotenv import load_dotenv
import imaplib
import os
import email
import json
from datetime import datetime
import socket 
import ssl

load_dotenv('../../.env')

# IMAP server details for Gmail
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# User credentials (replace with your own or use environment variables for security)
USERNAME = 'rubirubsen@gmail.com'
PASSWORD = os.getenv('MAIL_PASSWORD')

# Connect to the server
mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=60)
mail.login(USERNAME, PASSWORD)
mail.select('inbox')

status, messages = mail.search(None, 'UNSEEN')
emails = []
anzahlEmails = 0

try:
    for num in messages[0].split()[-20:]:  # Nur die letzten 100 E-Mails
        try:
            # E-Mail abrufen, ohne sie als gelesen zu markieren
            status, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extracting email details
                    subject = msg['subject']
                    from_ = msg['from']
                    date = msg['date']
                    
                    # Convert date to datetime object
                    date_object = email.utils.parsedate_to_datetime(date)
                    
                    email_info = {
                        "datetime_received": date_object.isoformat(),
                        "from": from_,
                        "subject": subject
                    }
                emails.append(email_info)
                
            # Optional: Sicherstellen, dass die E-Mail weiterhin als ungelesen markiert ist
            mail.store(num, '+FLAGS', '(\\Seen)')
            
            with open('emails.json', 'w') as json_file:
                json.dump(emails, json_file, indent=4)
            
        except (imaplib.IMAP4.error, socket.timeout, ssl.SSLError) as e:
            print(f"Ein Fehler ist beim Abrufen der E-Mail aufgetreten: {e}")
            continue
        print("new email found")
        anzahlEmails = anzahlEmails+1
except KeyboardInterrupt:
    print("Skript wurde vom Benutzer unterbrochen.")
finally:
    print(f"Alle {anzahlEmails} Emails abgerufen")
    mail.close()
    mail.logout()