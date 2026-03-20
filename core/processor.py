from core.builders import (construir_filas, construir_contexto, construir_comentario)
from utils.metrics_utils import (calcular_kpis, calcular_estado, calcular_color, analizar_anomalias)
from services.chart_service import (grafico_linea, grafico_boxplot, grafico_cumplimiento_pro, grafico_semanal)
from config import VERDE, ROJO

def extraer_datos_base(grupo, resumen, agente):
  nombre = grupo['Nombre'].iat[0]
  email = grupo['Email'].iat[0]
  horas_min = grupo['Horas minimas'].iat[0]
  total = resumen[agente]

  return {
    "nombre": nombre,
    "email": email,
    "horas_min": horas_min,
    "total": total,
    "diff": total - horas_min
  }

def generar_graficos(grupo, kpis):
  return (
    grafico_linea(grupo),
    grafico_semanal(grupo),
    grafico_boxplot(grupo),
    grafico_cumplimiento_pro(kpis['cumplimiento_pct'])
  )

def procesar_agente(agente, grupo, resumen, config):
  if grupo.empty:
    raise ValueError(f"Grupo vacío: {agente}")
  
  datos = extraer_datos_base(grupo, resumen, agente)

  filas = construir_filas(grupo, datos["nombre"])

  kpis = calcular_kpis(grupo, datos["total"], datos["horas_min"])

  estado = calcular_estado(datos["diff"])
  color = calcular_color(datos["diff"], VERDE, 'fbe083', ROJO)

  anomalias = analizar_anomalias(grupo)
  comentario = construir_comentario(datos["diff"], anomalias)

  graficos = generar_graficos(grupo, kpis) if config['generar_graficos'] else ()

  context = construir_contexto(datos, kpis, estado, color, anomalias, comentario, filas, config)

  return context, datos["email"], datos["nombre"], graficos