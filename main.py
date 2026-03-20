import pandas as pd
import os
import datetime
import logging

from config import PATH_OUTPUTS, ROJO, VERDE, PERIODO
from utils.file_utils import reset_folder
from utils.text_utils import truncar
from utils.time_utils import convertir_horas
from data.loader import preparar_datos
from services.pdf_service import generar_pdf
from services.email_service import enviar_email

logging.basicConfig(
  filename='logs/envio.log',
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
  reset_folder(PATH_OUTPUTS)

  df = preparar_datos()
  resumen = df.groupby('Agente')['Trabajó'].sum()  

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
        'periodo': PERIODO,
        'nombre_empleado': nombre,
        'horas_trabajadas': convertir_horas(total),
        'horas_minimas': convertir_horas(horas_min),
        'horas_trabajadas_list': filas,
        'diferencia': convertir_horas(diff),
        'color': color
      }

      ruta_pdf = os.path.join(PATH_OUTPUTS, f"RESUMEN_{nombre}.pdf")

      generar_pdf(context, ruta_pdf)

      """ if pd.notna(email):
        enviar_email(email, ruta_pdf, nombre, PERIODO)
        logging.info(f"OK - {email}")
      else:
        logging.warning(f"Sin email - {nombre}") """

    except Exception as e:
      logging.error(f"ERROR - {agente} - {str(e)}")

if __name__ == '__main__':
  main()