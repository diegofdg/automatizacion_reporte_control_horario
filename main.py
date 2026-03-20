import pandas as pd
import shutil
import os
import datetime
import unicodedata
import tempfile
import logging
import ssl
import smtplib

from docxtpl import DocxTemplate
from docx2pdf import convert
from email.message import EmailMessage

# ================== CONFIG ==================

MES_TRABAJO = "abril_2024"

BASE_DIR = os.path.dirname(__file__)
PATH_INPUT = os.path.join(BASE_DIR, 'inputs')
PATH_OUTPUT = os.path.join(BASE_DIR, 'outputs')

REPORTE_CSV = os.path.join(PATH_INPUT, f"reporte_asistencias_{MES_TRABAJO}.csv")
EMPLEADOS_CSV = os.path.join(PATH_INPUT, f"listado_empleados_{MES_TRABAJO}.csv")
PLANTILLA = os.path.join(PATH_INPUT, "plantilla_horas.docx")

EMAIL_EMISOR = 'diegofdg@gmail.com'
EMAIL_PASSWORD = 'pqgo bnwr sbug igrx'

TEST_MODE = True
EMAIL_TEST = "diegofdg@gmail.com"

ROJO = 'ec7c7b'
VERDE = '48bf91'
AMARILLO_COLOR = 'fbe083'
AZUL_COLOR = '4db4d7'

# ================== LOGGING ==================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename='logs/envio.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================== UTILS ==================

def reset_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def normalizar(texto):
    texto = str(texto).replace(',', '').upper()
    texto = unicodedata.normalize('NFD', texto)
    return texto.encode('ascii', 'ignore').decode('utf-8')

def convertir_horas(td):
    if pd.isna(td):
        return "00:00:00"
    total = int(td.total_seconds())
    return f"{total//3600:02}:{(total%3600)//60:02}:{total%60:02}"

def truncar(texto, max_len=44):
    texto = str(texto)
    return texto if len(texto) <= max_len else texto[:max_len-3] + "..."

def detectar_periodo(path):
    base = os.path.basename(path)
    return base.replace("reporte_asistencias_", "").replace(".csv", "").replace("_", " ").upper()

# ================== PDF ==================

def generar_pdf(context, ruta_pdf):
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        temp_docx = tmp.name

    try:
        doc = DocxTemplate(PLANTILLA)
        doc.render(context)
        doc.save(temp_docx)

        convert(temp_docx, ruta_pdf)

    finally:
        if os.path.exists(temp_docx):
            os.remove(temp_docx)

# ================== EMAIL ==================

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

# ================== PROCESAMIENTO ==================

def preparar_datos():

    df = pd.read_csv(REPORTE_CSV)
    df['Trabajó'] = pd.to_timedelta(df['Trabajó'], errors='coerce').fillna(pd.Timedelta(0))
    df['Día'] = pd.to_datetime(df['Día'], dayfirst=True)

    df = df[df['Detalle'] != "NO HAY REGISTRO"]

    emp = pd.read_csv(EMPLEADOS_CSV)
    emp['Horas minimas'] = pd.to_timedelta(emp['Horas minimas'], errors='coerce')

    df = df.merge(emp[['Agente', 'Email', 'Controla', 'Horas minimas']], on='Agente', how='left')
    df = df[df['Controla'] == True]

    df['Nombre'] = df['Agente'].apply(normalizar)

    return df

# ================== MAIN ==================

def main():

    reset_folder(PATH_OUTPUT)

    df = preparar_datos()
    resumen = df.groupby('Agente')['Trabajó'].sum()

    periodo = detectar_periodo(REPORTE_CSV)

    for agente, grupo in df.groupby('Agente'):

        try:
            nombre = grupo['Nombre'].iloc[0]
            email = grupo['Email'].iloc[0]
            horas_min = grupo['Horas minimas'].iloc[0]

            filas = [
                {
                    'Fecha': f.Día.strftime('%d/%m/%Y'),
                    'Nombre': nombre,
                    'Legajo': str(f.Legajo),
                    'Entrada': str(f.Entrada),
                    'Salida': str(f.Salida),
                    'Detalle': truncar(f.Detalle),
                    'Trabajo': convertir_horas(f.Trabajó)
                }
                for f in grupo.itertuples()
            ]

            total = resumen[agente]
            diff = total - horas_min

            color = VERDE if diff > datetime.timedelta(0) else ROJO if diff < datetime.timedelta(0) else ''

            context = {
                'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
                'periodo': periodo,
                'nombre_empleado': nombre,
                'horas_trabajadas': convertir_horas(total),
                'horas_minimas': convertir_horas(horas_min),
                'horas_trabajadas_list': filas,
                'diferencia': convertir_horas(diff),
                'color': color
            }

            ruta_pdf = os.path.join(PATH_OUTPUT, f"RESUMEN_{nombre}.pdf")

            generar_pdf(context, ruta_pdf)

            if pd.notna(email):
                enviar_email(email, ruta_pdf, nombre, periodo)
                logging.info(f"OK - {email}")
            else:
                logging.warning(f"Sin email - {nombre}")

        except Exception as e:
            logging.error(f"ERROR - {agente} - {str(e)}")

# ================== RUN ==================

if __name__ == '__main__':
  main()