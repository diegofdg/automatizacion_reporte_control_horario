import pandas as pd
from config import REPORTE_CSV, EMPLEADOS_CSV
from utils.text_utils import normalizar

def preparar_datos():
  df = pd.read_csv(REPORTE_CSV)
  df['Trabajó'] = pd.to_timedelta(df['Trabajó'], errors='coerce').fillna(pd.Timedelta(0))
  df['Día'] = pd.to_datetime(df['Día'], dayfirst=True)

  df = df[df['Detalle'] != "NO HAY REGISTRO"]

  emp = pd.read_csv(EMPLEADOS_CSV)
  emp['Horas minimas'] = pd.to_timedelta(emp['Horas minimas'], errors='coerce')

  df = df.merge(emp[['Agente', 'Email', 'Controla', 'Horas minimas']], on='Agente', how='left')
  df = df[df['Controla'] == True]

  df['Nombre'] = df['Agente'].apply(normalizar)

  return df