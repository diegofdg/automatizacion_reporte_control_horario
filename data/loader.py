import os
import logging
import pandas as pd

from config import PATH_INPUTS
from utils.text_utils import normalizar

def get_paths(config):
  reporte = os.path.join(PATH_INPUTS, f"reporte_asistencias_{config['periodo']}.csv")
  empleados = os.path.join(PATH_INPUTS, f"listado_empleados_{config['periodo']}.csv")
  return reporte, empleados

def validar_archivo(path):
  if not os.path.exists(path):
    raise FileNotFoundError(f"No existe archivo: {path}")

def preparar_datos(config):
  path_reporte, path_empleados = get_paths(config)

  validar_archivo(path_reporte)
  validar_archivo(path_empleados)

  df = pd.read_csv(path_reporte).copy()
  logging.info(f"Reporte cargado ({config['periodo']}): {len(df)} filas")

  df['Trabajó'] = pd.to_timedelta(df['Trabajó'], errors='coerce').fillna(pd.Timedelta(0))
  df['Día'] = pd.to_datetime(df['Día'], dayfirst=True, errors='coerce')

  df = df[df['Día'].notna()]

  df['Detalle'] = df['Detalle'].astype(str)
  df = df[~df['Detalle'].str.upper().str.contains("NO HAY REGISTRO", na=False)]

  emp = pd.read_csv(path_empleados).copy()

  emp['Horas minimas'] = pd.to_timedelta(emp['Horas minimas'], errors='coerce')
  emp['Controla'] = emp['Controla'].fillna(False)

  df = df.merge(
    emp[['Agente', 'Email', 'Controla', 'Horas minimas']],
    on='Agente',
    how='left'
  )

  faltantes = df['Email'].isna().sum()
  if faltantes > 0:
    logging.warning(f"{faltantes} registros sin email tras merge")

  df = df[df['Controla']]

  df['Nombre'] = df['Agente'].apply(normalizar)
  df['Horas minimas'] = df['Horas minimas'].fillna(pd.Timedelta(0))

  return df