from datetime import datetime
import os
import ssl
import smtplib
import logging

from email.message import EmailMessage

import pandas as pd
from config import EMAIL_EMISOR, EMAIL_PASSWORD, EMAIL_TEST, PATH_OUTPUTS
from services.report_service import generar_reportes

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

def enviar_email(destinatario, archivo, nombre, periodo):

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

  msg = crear_mensaje(destinatario, archivo, nombre, periodo)

  try:
    print(f"Enviando email: {nombre}")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
      smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
      smtp.send_message(msg)

    logging.info(f"Email enviado a: {destinatario_real}")
    return True

  except Exception as e:
    logging.error(f"Error enviando email a {destinatario_real}", exc_info=True)
    return False

def enviar_emails(config):
  path_envios = os.path.join(PATH_OUTPUTS, "envios.csv")

  if not os.path.exists(path_envios):
    print("⚠️ No existe envios.csv. Generando reportes primero...")
    generar_reportes(config)  

  df_envios = pd.read_csv(path_envios)
  df_envios['fecha_envio'] = df_envios['fecha_envio'].astype('object')

  if df_envios.empty:
    print("⚠️ No se generaron reportes. Revisar logs.")
    return
  
  for i, row in df_envios.iterrows():
    if row['enviado']:
      continue

    try:
      ruta = os.path.join(PATH_OUTPUTS, row['archivo'])

      destinatario = (
        EMAIL_TEST if config['test_mode'] else row['email']
      )

      if pd.isna(destinatario):
        logging.warning(f"Sin email - {row['nombre']}")
        continue

      enviar_email(destinatario, ruta, row['nombre'], config['periodo'])
      logging.info(f"Enviando email a: {destinatario}")

      df_envios.at[i, 'enviado'] = True
      df_envios.at[i, 'fecha_envio'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      logging.info(f"OK - {destinatario}")

    except Exception as e:
      logging.error(f"ERROR EMAIL - {row['nombre']}", exc_info=True)

  df_envios.to_csv(path_envios, index=False)