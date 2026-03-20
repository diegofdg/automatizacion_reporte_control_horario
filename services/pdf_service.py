import os
import tempfile
from docxtpl import DocxTemplate
from docx2pdf import convert
from config import PLANTILLA

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