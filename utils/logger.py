import logging
import os

def setup_logger(debug=False):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Evitar duplicados
    if logger.handlers:
        return logger

    # 📝 Formato PRO
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # 📁 Archivo
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # 🖥️ Consola (clave para debug en vivo)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger