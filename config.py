import os
from dotenv import load_dotenv

load_dotenv()

MES_TRABAJO = "abril_2024"
PERIODO = MES_TRABAJO.replace("_", " ").upper()

BASE_DIR = os.path.dirname(__file__)
PATH_INPUTS = os.path.join(BASE_DIR, 'inputs')
PATH_OUTPUTS = os.path.join(BASE_DIR, 'outputs')

REPORTE_CSV = os.path.join(PATH_INPUTS, f"reporte_asistencias_{MES_TRABAJO}.csv")
EMPLEADOS_CSV = os.path.join(PATH_INPUTS, f"listado_empleados_{MES_TRABAJO}.csv")
PLANTILLA = os.path.join(PATH_INPUTS, "plantilla_horas.docx")

EMAIL_EMISOR = os.getenv("EMAIL_EMISOR")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

TEST_MODE = True
EMAIL_TEST = "diegofdg@gmail.com"

ROJO = '#FF0000'
VERDE = '#008000'