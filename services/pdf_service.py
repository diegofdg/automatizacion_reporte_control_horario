import os
import tempfile
from docxtpl import DocxTemplate
from docxtpl import InlineImage
from docx.shared import Mm
from docx2pdf import convert
from config import PLANTILLA

def generar_pdf(context, ruta_pdf, graf1=None, graf2=None, graf3=None, graf4=None):
  with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
    temp_docx = tmp.name

  try:
    doc = DocxTemplate(PLANTILLA)
    if graf1:
      context['grafico1'] = InlineImage(doc, graf1, width=Mm(150))

    if graf2:
      context['grafico2'] = InlineImage(doc, graf2, width=Mm(150))

    if graf3:
      context['grafico3'] = InlineImage(doc, graf3, width=Mm(150))
    
    if graf4:
      context['grafico4'] = InlineImage(doc, graf4, width=Mm(150))

    doc.render(context)
    doc.save(temp_docx)

    convert(temp_docx, ruta_pdf)

  finally:
    if os.path.exists(temp_docx):
      os.remove(temp_docx)