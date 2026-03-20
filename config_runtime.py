import json
import os

CONFIG_PATH = "config_runtime.json"

DEFAULT_CONFIG = {
  "test_mode": True,
  "generar_graficos": False,
  "enviar_mails": False,
  "periodo": "abril_2024",
  "debug": False
}

def cargar_config():
  if not os.path.exists(CONFIG_PATH):
    guardar_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

  with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
  
  for k, v in DEFAULT_CONFIG.items():
    config.setdefault(k, v)
  return config

def guardar_config(config):
  with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)