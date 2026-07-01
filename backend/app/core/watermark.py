"""Lógica de inserción de marca de agua sobre imágenes usando Pillow.

Soporta dos disposiciones:
  - "Texto lineal": el texto se repite en una rejilla, rotado al ángulo indicado.
  - "Texto cruzado": el texto sigue una onda sinusoidal, rotando cada instancia
    según la tangente de la curva.

Opciones adicionales: tamaño de fuente, opacidad, modo de color (Actual /
Escala de grises) y redimensionado proporcional a 800px de ancho.
"""
import io
import math

from PIL import Image, ImageDraw, ImageFont

from app import config
from app.logging_config import setup_logger

logger = setup_logger(__name__)

TARGET_WIDTH = 800


def _load_font(font_size: int) -> ImageFont.FreeTypeFont:
    """Carga la fuente incluida en el proyecto; usa la de por defecto si falla."""
    try:
        return ImageFont.truetype(config.FONT_PATH, int(font_size))
    except Exception as exc:  # pragma: no cover - depende del entorno
        logger.warning("No se pudo cargar la fuente %s: %s", config.FONT_PATH, exc)
        return ImageFont.load_default()


def apply_watermark(
    image_bytes: bytes,
    *,
    text: str,
    font_size: int = 16,
    opacity: int = 125,
    watermark_type: str = "Texto lineal",
    text_angle: int = 0,
    color_mode: str = "Actual",
) -> bytes:
    """Aplica la marca de agua y devuelve los bytes de un PNG."""
    image = Image.open(io.BytesIO(image_bytes))

    # Asegurar modo RGBA para poder componer la marca de agua.
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    font = _load_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Variables comunes
    spacing_x = text_width * 2  # Espaciado horizontal
    spacing_y = text_height * 2  # Espaciado vertical
    rows = int(image.height / spacing_y) + 2
    cols = int(image.width / spacing_x) + 2
    color_value = 255 - opacity

    if watermark_type == "Texto lineal":
        # Crear patrón lineal
        angle = text_angle
        txt_template = Image.new(
            "RGBA", (int(text_width * 1.5), int(text_height * 1.5)), (255, 255, 255, 0)
        )
        d = ImageDraw.Draw(txt_template)
        d.text(
            (text_width / 4, text_height / 4),
            text,
            font=font,
            fill=(color_value, color_value, color_value, 255),
        )
        txt_template = txt_template.rotate(angle, expand=True)

        # Ajustar el espaciado según el ángulo para evitar superposición
        adjusted_spacing_x = spacing_x
        adjusted_spacing_y = spacing_y

        # Para ángulos cercanos a 90º, ajustar el espaciado horizontal y vertical
        if abs(angle) % 180 > 75 and abs(angle) % 180 < 105:
            adjusted_spacing_x = text_height * 2.5
            adjusted_spacing_y = text_width * 1.2
            rows = int(image.height / adjusted_spacing_y) + 4
            cols = int(image.width / adjusted_spacing_x) + 4

        # Calcular el área total a cubrir para asegurar que no queden huecos
        x_range = range(-2, cols + 3)
        y_range = range(-2, rows + 3)

        for row in y_range:
            for col in x_range:
                x = col * adjusted_spacing_x
                y = row * adjusted_spacing_y

                # Alternar filas para crear patrón diagonal
                if row % 2 == 0:
                    x += adjusted_spacing_x / 2

                paste_x = int(x)
                paste_y = int(y)
                if 0 <= paste_x < image.width and 0 <= paste_y < image.height:
                    image.paste(txt_template, (paste_x, paste_y), txt_template)

    elif watermark_type == "Texto cruzado":
        # Patrón sinusoidal: los textos siguen la forma de la onda.
        frequency = 0.005  # Frecuencia controlada para ondas visibles
        amplitude = text_height * 10.0  # Amplitud grande para ondas muy visibles
        wave_spacing_y = text_height * 8.0  # Espaciado vertical entre ondas

        # Cantidad de ondas para cubrir la imagen
        num_waves = max(3, int(image.height / (wave_spacing_y + amplitude * 2))) + 1

        # Espaciado horizontal basado en la frecuencia para evitar superposiciones
        period = 2 * math.pi / frequency  # Longitud de una onda completa en píxeles
        wave_spacing_x = period / 10  # 10 textos por onda completa

        for wave_idx in range(num_waves):
            wave_y_base = wave_idx * wave_spacing_y + image.height / (num_waves * 1.5)
            phase_offset = (wave_idx % 2) * math.pi
            num_texts = int(image.width / wave_spacing_x) + 8

            for i in range(-3, num_texts + 3):
                x_pos = i * wave_spacing_x

                # Posición Y siguiendo la onda sinusoidal
                wave_y = wave_y_base + amplitude * math.sin(
                    frequency * x_pos + phase_offset
                )

                # Ángulo tangente a la curva (derivada de sin(ax) es a*cos(ax))
                derivative = amplitude * frequency * math.cos(
                    frequency * x_pos + phase_offset
                )
                angle = math.degrees(math.atan(derivative))

                txt = Image.new(
                    "RGBA",
                    (int(text_width * 1.5), int(text_height * 1.5)),
                    (255, 255, 255, 0),
                )
                d = ImageDraw.Draw(txt)
                d.text(
                    (text_width / 4, text_height / 4),
                    text,
                    font=font,
                    fill=(color_value, color_value, color_value, 255),
                )
                txt = txt.rotate(angle, expand=True)

                paste_x = int(x_pos)
                paste_y = int(wave_y)
                if 0 <= paste_x < image.width and 0 <= paste_y < image.height:
                    image.paste(txt, (paste_x, paste_y), txt)

    # Aplanar sobre un fondo blanco.
    background = Image.new("RGB", image.size, (255, 255, 255))
    if image.mode == "RGBA":
        background.paste(image, mask=image.split()[3])
    else:
        background.paste(image)

    # Convertir a escala de grises si procede.
    if color_mode == "Escala de grises":
        background = background.convert("L").convert("RGB")

    if background.mode != "RGB":
        background = background.convert("RGB")

    # Redimensionar manteniendo la proporción (solo si supera el ancho objetivo).
    original_width, original_height = background.size
    ratio = original_width / TARGET_WIDTH if original_width > TARGET_WIDTH else 1
    if ratio > 1:
        target_height = int(original_height / ratio)
        background = background.resize(
            (TARGET_WIDTH, target_height), Image.Resampling.LANCZOS
        )

    buffered = io.BytesIO()
    background.save(buffered, format="PNG")
    buffered.seek(0)
    return buffered.getvalue()
