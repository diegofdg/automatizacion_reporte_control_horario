import os
import ssl
import smtplib
import logging

from email.message import EmailMessage
from config import EMAIL_EMISOR, EMAIL_PASSWORD, EMAIL_TEST


# =========================
# 🧰 HELPERS
# =========================

def validar_email(email):
    return email and isinstance(email, str) and "@" in email


def validar_archivo(path):
    return path and os.path.exists(path)


def crear_mensaje(destinatario, archivo, nombre, periodo):
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

    return msg


# =========================
# 📧 ENVIO
# =========================

def enviar_email(destinatario, archivo, nombre, periodo):

    # =========================
    # 🔐 VALIDACIONES
    # =========================

    if not EMAIL_EMISOR or not EMAIL_PASSWORD:
        logging.error("Credenciales de email no configuradas")
        return False

    if not validar_email(destinatario):
        logging.warning(f"Email inválido: {destinatario}")
        return False

    if not validar_archivo(archivo):
        logging.error(f"Archivo no encontrado: {archivo}")
        return False

    destinatario_real = destinatario

    # =========================
    # 🧾 CREAR MENSAJE
    # =========================

    msg = crear_mensaje(destinatario, archivo, nombre, periodo)

    # =========================
    # 🚀 ENVIO
    # =========================

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logging.info(f"Email enviado a: {destinatario_real}")
        return True

    except Exception as e:
        logging.error(f"Error enviando email a {destinatario_real}", exc_info=True)
        return False