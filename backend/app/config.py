"""Configuración de la aplicación vía variables de entorno."""
import os

VERSION = os.getenv("VERSION", "dev")
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "static"))
FONT_PATH = os.getenv(
    "FONT_PATH",
    os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf"),
)
