import os
import tempfile
import logging

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx2pdf import convert

from config import PLANTILLA

DEBUG_DOCX = True

def crear_doc_temp():
  tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
  path = tmp.name
  tmp.close()
  return path


def agregar_graficos(doc, context, graficos):
  """
  Inserta gráficos dinámicamente en el contexto:
  grafico1, grafico2, etc.
  """
  for i, graf in enumerate(graficos, start=1):
    if graf and os.path.exists(graf):
      context[f'grafico{i}'] = InlineImage(doc, graf, width=Mm(150))
    else:
      context[f'grafico{i}'] = ""

def generar_pdf(context, ruta_pdf, *graficos):
  temp_docx = crear_doc_temp()

  try:
    context = context.copy()
    doc = DocxTemplate(PLANTILLA)
    agregar_graficos(doc, context, graficos)
    doc.render(context)
    doc.save(temp_docx)
    convert(temp_docx, ruta_pdf)

    logging.info(f"PDF generado: {ruta_pdf}")

  except Exception as e:
    logging.error(f"Error generando PDF: {ruta_pdf}", exc_info=True)

    if DEBUG_DOCX:
      debug_path = ruta_pdf.replace(".pdf", "_DEBUG.docx")
      try:
        doc.save(debug_path)
        logging.info(f"DOCX debug guardado: {debug_path}")
      except:
        logging.error("No se pudo guardar DOCX de debug")
    raise e

  finally:
    if os.path.exists(temp_docx):
      os.remove(temp_docx)