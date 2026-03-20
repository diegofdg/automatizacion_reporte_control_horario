import os
import ssl
import smtplib
from email.message import EmailMessage
from config import EMAIL_EMISOR, EMAIL_PASSWORD, TEST_MODE, EMAIL_TEST

def enviar_email(destinatario, archivo, nombre, periodo):

    if TEST_MODE:
        destinatario = EMAIL_TEST

    msg = EmailMessage()
    msg['From'] = EMAIL_EMISOR
    msg['To'] = destinatario
    msg['Subject'] = f"Reporte de horas - {periodo}"

    msg.set_content(f"""
Hola {nombre},

Adjunto encontrarás tu reporte de horas correspondiente a {periodo}.

Saludos.
""")

    with open(archivo, 'rb') as f:
        msg.add_attachment(
            f.read(),
            maintype='application',
            subtype='pdf',
            filename=os.path.basename(archivo)
        )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
        smtp.send_message(msg)