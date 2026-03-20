import logging
from utils.logger import setup_logger
from config_runtime import cargar_config, guardar_config
from services.report_service import generar_reportes
from services.email_service import enviar_emails

logging.basicConfig(
  filename='logs/envio.log',
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

def mostrar_menu():
  print("\n===== SISTEMA DE REPORTES =====")
  print("1 - Configurar aplicación")
  print("2 - Generar reportes")
  print("3 - Enviar emails")
  print("0 - Salir")

  opcion = input("Seleccioná una opción: ")
  return opcion

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

def main():
  config = cargar_config()
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