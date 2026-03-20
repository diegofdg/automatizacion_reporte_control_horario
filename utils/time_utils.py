import pandas as pd

def convertir_horas(td):
  if pd.isna(td):
    return "00:00:00"
  total = int(td.total_seconds())
  return f"{total//3600:02}:{(total%3600)//60:02}:{total%60:02}"