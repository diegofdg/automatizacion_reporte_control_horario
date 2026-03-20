import pandas as pd
import datetime

def calcular_kpis(grupo, total, horas_min):

  dias_trabajados = grupo[grupo['Trabajó'] > pd.Timedelta(0)]['Día'].nunique()

  promedio = total / dias_trabajados if dias_trabajados else pd.Timedelta(0)
  max_dia = grupo['Trabajó'].max()
  min_dia = grupo['Trabajó'].min()

  cumplimiento = (total / horas_min) if horas_min != pd.Timedelta(0) else 0

  return {
    'dias_trabajados': dias_trabajados,
    'promedio': promedio,
    'max_dia': max_dia,
    'min_dia': min_dia,
    'cumplimiento_pct': cumplimiento
  }


def calcular_estado(diff):
  if diff >= datetime.timedelta(0):
    return "OK"
  elif diff >= -datetime.timedelta(hours=2):
    return "LEVE DESVÍO"
  else:
    return "CRÍTICO"


def calcular_color(diff, VERDE, AMARILLO, ROJO):
  if diff >= datetime.timedelta(0):
    return VERDE
  elif diff >= -datetime.timedelta(hours=2):
    return AMARILLO
  else:
    return ROJO


def analizar_anomalias(grupo):
    dias_bajos = (grupo['Trabajó'] < pd.Timedelta(hours=4)).sum()
    dias_altos = (grupo['Trabajó'] > pd.Timedelta(hours=10)).sum()
    dias_cero = (grupo['Trabajó'] == pd.Timedelta(0)).sum()

    faltas_registro = grupo['Detalle'].str.contains(
        'FALTA REGISTRO DE ENTRADA O SALIDA',
        case=False,
        na=False
    ).sum()

    return {
        'dias_bajos': dias_bajos,
        'dias_altos': dias_altos,
        'dias_cero': dias_cero,
        'faltas_registro': faltas_registro
    }


def generar_comentario(diff, dias_bajos):
    if diff > datetime.timedelta(0):
        return "Excelente desempeño, superó las horas requeridas."
    elif dias_bajos > 3:
        return "Se detectan múltiples jornadas sin asistencia. Se recomienda revisión."
    elif diff < datetime.timedelta(0):
        return "No se alcanzaron las horas mínimas."
    else:
        return "Cumplimiento correcto."