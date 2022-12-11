from pathlib import Path
import json
import os, sys #for file paths
sys.path.insert(0, str(Path(__file__).resolve().parent))

dir = os.getcwd()
i = dir.rfind('/')
DOWNLOAD_DIR = dir[:i]

with open(DOWNLOAD_DIR+"/json/settings.json", "r") as fn:
    db = json.load(fn)
print(db)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
#from email import encoders
from email.encoders import encode_base64

def sendEmail(receiver, name, docname):
    body = f'''Hello,
    {name}
    '''
    # put your email here
    sender = db["EmailUsername"]
    password = db['EmailPassword']
    message = MIMEMultipart()
    
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'Group1 Receipt'

    message.attach(MIMEText(body, 'plain'))

    binary_pdf = open(docname, 'rb')

    payload = MIMEBase('application', 'octate-stream', Name="receipt.docx")
    # payload = MIMEBase('application', 'pdf', Name=docname)
    payload.set_payload((binary_pdf).read())

    # enconding the binary into base64
    encode_base64(payload)

    # add header with pdf name
    payload.add_header('Content-Decomposition', 'attachment', filename="receipt.docx")
    message.attach(payload)

    #use gmail with port
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    #enable security
    session.starttls()

    #login with mail_id and password
    session.login(sender, password)

    text = message.as_string()
    session.sendmail(sender, receiver, text)
    session.quit()
    print('Mail Sent')
