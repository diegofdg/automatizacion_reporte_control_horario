import unicodedata
from docxtpl import RichText

FALTA_TEXTO = 'FALTA REGISTRO DE ENTRADA O SALIDA'

def contiene(texto, patron):
  if not texto:
    return False
  return patron in str(texto).upper()

def es_falta(detalle):
  return contiene(detalle, FALTA_TEXTO)

def normalizar(texto):
  if texto is None:
    return ""

  texto = str(texto).strip()
  texto = unicodedata.normalize('NFD', texto)
  texto = texto.encode('ascii', 'ignore').decode('utf-8')
  texto = texto.replace(',', '').upper()

  return texto


def truncar(texto, max_len=44):
  if texto is None:
    return ""

  texto = str(texto)

  if max_len <= 3:
    return texto[:max_len]

  return texto if len(texto) <= max_len else texto[:max_len - 3] + "..."


def texto_coloreado(valor, color, bold=True):
  rt = RichText()
  rt.add(str(valor), color=color, bold=bold)
  return rt
