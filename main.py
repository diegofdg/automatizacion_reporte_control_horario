import pandas as pd
import os
import datetime
import logging
import traceback

from config import PATH_OUTPUTS, ROJO, VERDE, PERIODO, GENERAR_GRAFICOS
from utils.file_utils import reset_folder
from utils.text_utils import truncar, texto_coloreado, es_falta
from utils.time_utils import convertir_horas
from data.loader import preparar_datos
from services.pdf_service import generar_pdf
from services.email_service import enviar_email

from utils.metrics_utils import calcular_kpis, calcular_estado, calcular_color, analizar_anomalias, generar_comentario
from services.chart_service import grafico_barras, grafico_histograma, grafico_semana, grafico_cumplimiento, grafico_linea, grafico_semana_pro, grafico_boxplot, grafico_cumplimiento_pro, grafico_semanal

def procesar_agente(agente, grupo, resumen):
  first = grupo.iloc[0]
  nombre = first['Nombre']
  email = first['Email']
  horas_min = first['Horas minimas']

  total = resumen[agente]
  diff = total - horas_min

  filas = construir_filas(grupo, nombre)

  kpis = calcular_kpis(grupo, total, horas_min)
  estado = calcular_estado(diff)
  color = calcular_color(diff, VERDE, 'fbe083', ROJO)

  anomalias = analizar_anomalias(grupo)
  comentario = construir_comentario(diff, anomalias)

  graficos = generar_graficos(grupo, kpis)

  context = construir_contexto(
    nombre, total, horas_min, diff,
    kpis, estado, color, anomalias,
    comentario, filas
  )

  return context, email, nombre, graficos

def construir_filas(grupo, nombre):
  return [
    {
      'Fecha': f.Día.strftime('%d/%m/%Y'),
      'Nombre': nombre,
      'Legajo': str(f.Legajo),
      'Entrada': str(f.Entrada),
      'Salida': str(f.Salida),
      'Detalle': formatear_detalle(f.Detalle),
      'Trabajo': convertir_horas(f.Trabajó)
    }
    for f in grupo.itertuples()
  ]

def formatear_detalle(detalle):
  falta = es_falta(detalle)
  color = "#FF0000" if falta else "#000000"
  return texto_coloreado(truncar(detalle), color, falta)

def construir_comentario(diff, anomalias):
  comentario = generar_comentario(diff, anomalias['dias_bajos'])

  if anomalias['faltas_registro'] > 0:
    comentario += f" Se detectaron {anomalias['faltas_registro']} días con faltas de registro."

  return comentario

def construir_contexto(nombre, total, horas_min, diff, kpis, estado, color, anomalias, comentario, filas):
  

  return {
    'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
    'periodo': PERIODO,
    'nombre_empleado': nombre,

    'horas_trabajadas': texto_coloreado(convertir_horas(total), color),
    'horas_minimas': convertir_horas(horas_min),
    'diferencia': texto_coloreado(convertir_horas(diff), color),

    'faltas_registro': anomalias['faltas_registro'],

    'estado': estado,
    'color': color,

    'cumplimiento': f"{kpis['cumplimiento_pct'] * 100:.0f}%",
    'dias_trabajados': kpis['dias_trabajados'],
    'promedio': convertir_horas(kpis['promedio']),
    'max_dia': convertir_horas(kpis['max_dia']),
    'min_dia': convertir_horas(kpis['min_dia']),

    'dias_bajos': anomalias['dias_bajos'],
    'dias_altos': anomalias['dias_altos'],
    'dias_cero': anomalias['dias_cero'],

    'comentario': comentario,

    'horas_trabajadas_list': filas
  }



logging.basicConfig(
  filename='logs/envio.log',
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

def generar_graficos(grupo, kpis):
  if not GENERAR_GRAFICOS:
    return None, None, None, None

  return (
    grafico_linea(grupo),
    grafico_semanal(grupo),
    grafico_boxplot(grupo),
    grafico_cumplimiento_pro(kpis['cumplimiento_pct'])
  )

def construir_contexto(nombre, total, horas_min, diff, kpis, estado, color, anomalias, comentario, filas):
  cumplimiento = f"{kpis['cumplimiento_pct'] * 100:.0f}%"
  return {
    'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
    'periodo': PERIODO,
    'nombre_empleado': nombre,

    'horas_trabajadas': texto_coloreado(convertir_horas(total), color),
    'horas_minimas': convertir_horas(horas_min),
    'diferencia': texto_coloreado(convertir_horas(diff), color),

    'faltas_registro': anomalias['faltas_registro'],

    'estado': estado,
    'color': color,

    'cumplimiento': cumplimiento,
    'dias_trabajados': kpis['dias_trabajados'],
    'promedio': convertir_horas(kpis['promedio']),
    'max_dia': convertir_horas(kpis['max_dia']),
    'min_dia': convertir_horas(kpis['min_dia']),

    'dias_bajos': anomalias['dias_bajos'],
    'dias_altos': anomalias['dias_altos'],
    'dias_cero': anomalias['dias_cero'],

    'comentario': comentario,

    'horas_trabajadas_list': filas
  }

def main():
  reset_folder(PATH_OUTPUTS)

  df = preparar_datos()
  resumen = df.groupby('Agente')['Trabajó'].sum()

  for agente, grupo in df.groupby('Agente'):
    try:
      context, email, nombre, graficos = procesar_agente(agente, grupo, resumen)

      ruta_pdf = os.path.join(PATH_OUTPUTS, f"RESUMEN_{nombre}.pdf")

      generar_pdf(context, ruta_pdf, *graficos)

    except Exception as e:
      logging.error(f"ERROR - {agente}", exc_info=True)
      print(traceback.format_exc())

if __name__ == '__main__':
  main()