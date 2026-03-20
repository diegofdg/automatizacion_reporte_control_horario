import os
from dotenv import load_dotenv

load_dotenv()

# ================== PATHS ==================

BASE_DIR = os.path.dirname(__file__)
PATH_INPUTS = os.path.join(BASE_DIR, 'inputs')
PATH_OUTPUTS = os.path.join(BASE_DIR, 'outputs')

PLANTILLA = os.path.join(PATH_INPUTS, "plantilla_horas.docx")

# ================== EMAIL ==================

EMAIL_EMISOR = os.getenv("EMAIL_EMISOR")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TEST = os.getenv("EMAIL_TEST")

# ================== COLORES ==================

ROJO = '#FF0000'
VERDE = '#008000'
AMARILLO = '#fbe083'