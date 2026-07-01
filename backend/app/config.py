"""Configuración de la aplicación vía variables de entorno."""
import os

VERSION = os.getenv("VERSION", "dev")
DEBUG = int(os.getenv("DEBUG", "0"))
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "static"))
FONT_PATH = os.getenv(
    "FONT_PATH",
    os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf"),
)
