import os
import pandas as pd
import logging

from config import PATH_OUTPUTS
from utils.file_utils import reset_folder
from data.loader import preparar_datos
from services.pdf_service import generar_pdf

from core.processor import procesar_agente

def generar_reportes(config):
  reset_folder(PATH_OUTPUTS)

  df = preparar_datos(config)
  
  if df.empty:
    print("❌ DataFrame vacío")
    return
  
  resumen = df.groupby('Agente')['Trabajó'].sum()

  registros = []

  for agente, grupo in df.groupby('Agente'):
    try:
      context, email, nombre, graficos = procesar_agente(agente, grupo, resumen, config)
      print(f"Procesando agente: {nombre}")
      
      archivo = f"RESUMEN_{nombre}.pdf"
      ruta_pdf = os.path.join(PATH_OUTPUTS, archivo)

      if graficos:
        generar_pdf(context, ruta_pdf, *graficos)
      else:
        generar_pdf(context, ruta_pdf)

      registros.append({
        "nombre": nombre,
        "email": email,
        "archivo": archivo,
        "enviado": False,
        "fecha_envio": ""
      })

    except Exception as e:
      logging.exception(f"Error procesando agente: {agente}")
      print(f"❌ Error en {agente}: {e}")
  
  if not registros:
    print("⚠️ No se generaron reportes. Revisar logs.")
    return
  df_envios = pd.DataFrame(registros)
  df_envios.to_csv(os.path.join(PATH_OUTPUTS, "envios.csv"), index=False)

  print("Registros generados:", len(registros))