import pandas as pd
from datetime import datetime

from utils.metrics_utils import generar_comentario
from utils.text_utils import es_falta, texto_coloreado, truncar
from utils.time_utils import convertir_horas

def construir_filas(grupo, nombre):
  return [
    {
      'Fecha': f.Día.strftime('%d/%m/%Y') if pd.notna(f.Día) else '',
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

def construir_contexto(datos, kpis, estado, color, anomalias, comentario, filas, config):
  cumplimiento = f"{kpis['cumplimiento_pct'] * 100:.0f}%"

  return {
    'fecha': datetime.now().strftime("%d/%m/%Y"),
    'periodo': config['periodo'],
    'nombre_empleado': datos["nombre"],

    'horas_trabajadas': texto_coloreado(convertir_horas(datos["total"]), color),
    'horas_minimas': convertir_horas(datos["horas_min"]),
    'diferencia': texto_coloreado(convertir_horas(datos["diff"]), color),

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