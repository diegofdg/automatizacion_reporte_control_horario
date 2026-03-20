import pandas as pd
import os
from datetime import datetime
import logging
import traceback
from utils.logger import setup_logger

from config import PATH_OUTPUTS, ROJO, VERDE, EMAIL_TEST
from utils.file_utils import reset_folder
from utils.text_utils import truncar, texto_coloreado, es_falta
from utils.time_utils import convertir_horas
from data.loader import preparar_datos
from services.pdf_service import generar_pdf
from services.email_service import enviar_email

from utils.metrics_utils import calcular_kpis, calcular_estado, calcular_color, analizar_anomalias, generar_comentario
from services.chart_service import grafico_linea, grafico_boxplot, grafico_cumplimiento_pro, grafico_semanal

from config_runtime import cargar_config, guardar_config


def mostrar_menu():
  print("\n===== SISTEMA DE REPORTES =====")
  print("1 - Configurar aplicación")
  print("2 - Generar reportes")
  print("3 - Enviar emails")
  print("0 - Salir")

  opcion = input("Seleccioná una opción: ")
  return opcion

def generar_reportes(config):
    reset_folder(PATH_OUTPUTS)

    registros = []

    df = preparar_datos(config)
    print("Filas totales:", len(df))

    if df.empty:
        print("❌ DataFrame vacío")
        return

    print("Agentes:", df['Agente'].nunique())
    resumen = df.groupby('Agente')['Trabajó'].sum()

    for agente, grupo in df.groupby('Agente'):
        print("DEBUG agente:", agente)
        print(grupo.head())
        try:
            print("Entrando a procesar_agente")
            context, email, nombre, graficos = procesar_agente(
                agente, grupo, resumen, config
            )
            logging.info(f"Generando PDF: {nombre}")
            print("Generando PDF...")

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
                "fecha_envio": None
            })

        except Exception:
            logging.exception(f"Error procesando agente: {agente}")

    # ✅ FUERA DEL LOOP
    df_envios = pd.DataFrame(registros)
    if df_envios.empty:
        print("⚠️ No se generaron reportes. Revisar logs.")
        return
    df_envios.to_csv(os.path.join(PATH_OUTPUTS, "envios.csv"), index=False)

    print("Registros generados:", len(registros))

def enviar_emails(config):
  path_envios = os.path.join(PATH_OUTPUTS, "envios.csv")

  if not os.path.exists(path_envios):
    print("⚠️ No existe envios.csv. Generando reportes primero...")
    generar_reportes(config)
  

  df_envios = pd.read_csv(path_envios)

  if df_envios.empty:
      print("⚠️ No se generaron reportes. Revisar logs.")
      return
  
  for i, row in df_envios.iterrows():
    if row['enviado']:
      continue

    try:
      ruta = os.path.join(PATH_OUTPUTS, row['archivo'])

      destinatario = (
        EMAIL_TEST if config['test_mode'] else row['email']
      )

      if pd.isna(destinatario):
        logging.warning(f"Sin email - {row['nombre']}")
        continue

      enviar_email(destinatario, ruta, row['nombre'], config['periodo'])
      logging.info(f"Enviando email a: {destinatario}")

      df_envios.at[i, 'enviado'] = True
      df_envios.at[i, 'fecha_envio'] = datetime.now()
      logging.info(f"OK - {destinatario}")

    except Exception as e:
      logging.error(f"ERROR EMAIL - {row['nombre']}", exc_info=True)

  # ✅ actualizar archivo
  df_envios.to_csv(path_envios, index=False)

def configurar():
  config = cargar_config()

  print("\n--- CONFIGURACIÓN ---")

  test = input(f"Modo TEST? (s/n) [{config['test_mode']}]: ").lower()
  if test:
    config['test_mode'] = test == 's'

  debug = input(f"Modo DEBUG? (s/n) [{config.get('debug', False)}]: ").lower()
  if debug:
    config['debug'] = debug == 's'

  graficos = input(f"Generar gráficos? (s/n) [{config['generar_graficos']}]: ").lower()
  if graficos:
    config['generar_graficos'] = graficos == 's'

  enviar = input(f"Enviar emails? (s/n) [{config['enviar_mails']}]: ").lower()
  if enviar:
    config['enviar_mails'] = enviar == 's'

  mes = input("Mes (ej: 04): ")
  anio = input("Año (ej: 2024): ")

  meses = {
    "01": "enero", "02": "febrero", "03": "marzo",
    "04": "abril", "05": "mayo", "06": "junio",
    "07": "julio", "08": "agosto", "09": "septiembre",
    "10": "octubre", "11": "noviembre", "12": "diciembre"
  }

  if mes and anio and mes in meses:
    config['periodo'] = f"{meses[mes]}_{anio}"
    print(f"Periodo actualizado: {config['periodo']}")

  guardar_config(config)

  return config


def procesar_agente(agente, grupo, resumen, config):
    try:
        first = grupo.iloc[0]
        nombre = first['Nombre']
        email = first['Email']
        horas_min = first['Horas minimas']

        total = resumen[agente]

        print("DEBUG total:", total, type(total))
        print("DEBUG horas_min:", horas_min, type(horas_min))

        diff = total - horas_min

        print("DEBUG diff:", diff)

        filas = construir_filas(grupo, nombre)
        print("DEBUG filas OK")

        kpis = calcular_kpis(grupo, total, horas_min)
        print("DEBUG kpis OK")

        estado = calcular_estado(diff)
        color = calcular_color(diff, VERDE, 'fbe083', ROJO)

        anomalias = analizar_anomalias(grupo)
        comentario = construir_comentario(diff, anomalias)

        graficos = generar_graficos(grupo, kpis) if config['generar_graficos'] else ()

        context = construir_contexto(
            nombre, total, horas_min, diff,
            kpis, estado, color, anomalias,
            comentario, filas, config
        )

        return context, email, nombre, graficos

    except Exception as e:
        print("🔥 ERROR REAL:", e)
        raise

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

logging.basicConfig(
  filename='logs/envio.log',
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

def generar_graficos(grupo, kpis):
  return (
    grafico_linea(grupo),
    grafico_semanal(grupo),
    grafico_boxplot(grupo),
    grafico_cumplimiento_pro(kpis['cumplimiento_pct'])
  )

def construir_contexto(nombre, total, horas_min, diff, kpis, estado, color, anomalias, comentario, filas, config):
  cumplimiento = f"{kpis['cumplimiento_pct'] * 100:.0f}%"
  return {
    'fecha': datetime.now().strftime("%d/%m/%Y"),
    'periodo': config['periodo'],
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

from config_runtime import cargar_config

def main():
  config = cargar_config()
  # 🔥 activar logging según config
  setup_logger(debug=config.get("debug", False))

  while True:
    opcion = mostrar_menu()

    if opcion == "1":
      config = configurar()

    elif opcion == "2":
      generar_reportes(config)

    elif opcion == "3":
      enviar_emails(config)

    elif opcion == "0":
      break

if __name__ == '__main__':
  main()