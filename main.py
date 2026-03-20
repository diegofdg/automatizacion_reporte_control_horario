import pandas as pd
import os
import datetime
import logging
import traceback

from config import PATH_OUTPUTS, ROJO, VERDE, PERIODO
from utils.file_utils import reset_folder
from utils.text_utils import truncar, texto_coloreado, es_falta
from utils.time_utils import convertir_horas
from data.loader import preparar_datos
from services.pdf_service import generar_pdf
from services.email_service import enviar_email

from utils.metrics_utils import calcular_kpis, calcular_estado, calcular_color, analizar_anomalias, generar_comentario
from services.chart_service import grafico_barras, grafico_histograma, grafico_semana

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
          'Detalle': (
            texto_coloreado(truncar(f.Detalle), "#FF0000")
            if es_falta(f.Detalle)
            else texto_coloreado(truncar(f.Detalle), "#000000", False)
          ),
          'Trabajo': convertir_horas(f.Trabajó)
        }
        
        for f in grupo.itertuples()
      ]

      total = resumen[agente]
      diff = total - horas_min

      kpis = calcular_kpis(grupo, total, horas_min)
      estado = calcular_estado(diff)
      color = calcular_color(diff, VERDE, 'fbe083', ROJO)

      anomalias = analizar_anomalias(grupo)
      comentario = generar_comentario(diff, anomalias['dias_bajos'])
      if anomalias['faltas_registro'] > 0:
        comentario += f" Se detectaron {anomalias['faltas_registro']} días con faltas de registro."
      graf1 = grafico_barras(grupo)
      graf2 = grafico_semana(grupo)
      graf3 = grafico_histograma(grupo)

      context = {
        'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
        'periodo': PERIODO,
        'nombre_empleado': nombre,

        'horas_trabajadas': texto_coloreado(convertir_horas(total), color),
        'horas_minimas': convertir_horas(horas_min),
        'diferencia': texto_coloreado(convertir_horas(diff), color),
        'faltas_registro': anomalias['faltas_registro'],

        'estado': estado,
        'color': color,

        # KPIs
        'cumplimiento': kpis['cumplimiento_pct'],
        'dias_trabajados': kpis['dias_trabajados'],
        'promedio': convertir_horas(kpis['promedio']),
        'max_dia': convertir_horas(kpis['max_dia']),
        'min_dia': convertir_horas(kpis['min_dia']),

        # Análisis
        'dias_bajos': anomalias['dias_bajos'],
        'dias_altos': anomalias['dias_altos'],
        'dias_cero': anomalias['dias_cero'],

        'comentario': comentario,

        'horas_trabajadas_list': filas
    }

      ruta_pdf = os.path.join(PATH_OUTPUTS, f"RESUMEN_{nombre}.pdf")

      generar_pdf(context, ruta_pdf, graf1, graf2, graf3)

      """ if pd.notna(email):
        enviar_email(email, ruta_pdf, nombre, PERIODO)
        logging.info(f"OK - {email}")
      else:
        logging.warning(f"Sin email - {nombre}") """

    except Exception as e:
      logging.error(f"ERROR - {agente} - {str(e)}")
      print(traceback.format_exc())  # 👈 CLAVE

if __name__ == '__main__':
  main()