import unicodedata
from docxtpl import RichText

def normalizar(texto):
  texto = str(texto).replace(',', '').upper()
  texto = unicodedata.normalize('NFD', texto)
  return texto.encode('ascii', 'ignore').decode('utf-8')

def truncar(texto, max_len=44):
  texto = str(texto)
  return texto if len(texto) <= max_len else texto[:max_len-3] + "..."

def texto_coloreado(valor, color, bold=True):
  rt = RichText()
  rt.add(valor, color=color, bold=bold)
  return rt

def es_falta(detalle):
  return 'FALTA REGISTRO DE ENTRADA O SALIDA' in str(detalle).upper()