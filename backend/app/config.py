"""Configuración de la aplicación vía variables de entorno."""
import os

VERSION = os.getenv("VERSION", "dev")
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "static"))

FONTS_DIR = os.getenv(
    "FONTS_DIR", os.path.join(os.path.dirname(__file__), "assets", "fonts")
)

# Fuente por defecto y compatibilidad con la variable FONT_PATH previa.
FONT_PATH = os.getenv("FONT_PATH", os.path.join(FONTS_DIR, "DejaVuSans.ttf"))

# Lista blanca de fuentes disponibles: nombre lógico -> fichero en FONTS_DIR.
# Se resuelve siempre contra FONTS_DIR para evitar path traversal.
FONTS = {
    # Sans serif
    "DejaVu Sans": "DejaVuSans.ttf",
    "Open Sans": "OpenSans-Regular.ttf",
    "Montserrat": "Montserrat-Regular.ttf",
    # Con serifa
    "DejaVu Serif": "DejaVuSerif.ttf",
    "PT Serif": "PTSerif-Regular.ttf",
    # Monoespaciada
    "DejaVu Sans Mono": "DejaVuSansMono.ttf",
    # Impacto / destacadas
    "DejaVu Sans Bold": "DejaVuSans-Bold.ttf",
    "Oswald": "Oswald-Regular.ttf",
    "Anton": "Anton-Regular.ttf",
}
DEFAULT_FONT_FAMILY = "DejaVu Sans Mono"
