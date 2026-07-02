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
import os

from PIL import Image, ImageDraw, ImageFont

from app import config
from app.logging_config import setup_logger

logger = setup_logger(__name__)

TARGET_WIDTH = 800


def _load_font(font_size: int, font_family: str = config.DEFAULT_FONT_FAMILY):
    """Carga una fuente de la lista blanca; cae a la de por defecto si falla.

    `font_family` es un nombre lógico (clave de `config.FONTS`), no una ruta:
    se resuelve siempre dentro de `config.FONTS_DIR` para evitar path traversal.
    """
    filename = config.FONTS.get(font_family)
    if filename is None:
        logger.warning("Fuente desconocida '%s'; se usa la de por defecto", font_family)
        filename = config.FONTS[config.DEFAULT_FONT_FAMILY]

    font_path = os.path.join(config.FONTS_DIR, filename)
    try:
        return ImageFont.truetype(font_path, int(font_size))
    except Exception as exc:  # pragma: no cover - depende del entorno
        logger.warning("No se pudo cargar la fuente %s: %s", font_path, exc)
        return ImageFont.load_default()


def _text_tile(font, text: str, fill: tuple[int, int, int, int]) -> Image.Image:
    """Crea un lienzo RGBA ajustado al texto, con el texto dibujado sin recortes.

    Dimensiona el lienzo a partir del bounding box real del texto (que puede tener
    origen negativo según la fuente) y dibuja compensando ese origen más un padding,
    de modo que ninguna fuente quede cortada por sus ascendentes o descendentes.
    """
    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    left, top, right, bottom = measure.textbbox((0, 0), text, font=font)
    pad = max(4, (bottom - top) // 2)
    tile = Image.new(
        "RGBA", (right - left + 2 * pad, bottom - top + 2 * pad), (255, 255, 255, 0)
    )
    ImageDraw.Draw(tile).text((pad - left, pad - top), text, font=font, fill=fill)
    return tile


def _parse_hex(color: str) -> tuple[int, int, int]:
    """Convierte un color '#rrggbb' (o 'rrggbb') a una tupla RGB.

    Ante un valor inválido devuelve gris medio, para no romper el procesado.
    """
    value = color.lstrip("#")
    try:
        if len(value) == 3:  # formato corto '#abc'
            value = "".join(c * 2 for c in value)
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return r, g, b
    except (ValueError, IndexError):
        logger.warning("Color inválido '%s'; se usa gris medio", color)
        return 128, 128, 128


def _paste_logo(
    base: Image.Image,
    logo_bytes: bytes,
    *,
    scale: int,
    opacity: int,
    position: str = "center",
) -> None:
    """Compone un logo sobre `base` (modo RGBA), in situ.

    `scale` es el ancho del logo como % del ancho de la imagen; `opacity` (0-255)
    modula su transparencia; `position` es una de las claves de `_anchor`.
    """
    logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

    scale = max(1, min(int(scale), 100))
    target_w = max(1, int(base.width * scale / 100))
    ratio = target_w / logo.width
    target_h = max(1, int(logo.height * ratio))
    logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Modular el canal alfa por la opacidad indicada.
    alpha = logo.split()[3].point(lambda a: int(a * max(0, min(opacity, 255)) / 255))
    logo.putalpha(alpha)

    margin = max(8, int(base.width * 0.02))
    pos = _anchor(position, base.width, base.height, logo.width, logo.height, margin)
    base.paste(logo, pos, logo)


def _anchor(
    position: str, cw: int, ch: int, ew: int, eh: int, margin: int
) -> tuple[int, int]:
    """Calcula la esquina superior-izquierda para colocar un elemento de tamaño
    (ew, eh) dentro de un contenedor (cw, ch) según `position`.

    Posiciones válidas: 'center' y las cuatro esquinas
    'top-left' / 'top-right' / 'bottom-left' / 'bottom-right'.
    Ante un valor desconocido usa el centro.
    """
    if position == "center" or "-" not in position:
        return (cw - ew) // 2, (ch - eh) // 2
    vert, _, horiz = position.partition("-")
    x = margin if horiz == "left" else cw - ew - margin
    y = margin if vert == "top" else ch - eh - margin
    return x, y


def apply_watermark(
    image_bytes: bytes,
    *,
    text: str,
    font_size: int = 16,
    opacity: int = 125,
    watermark_type: str = "Texto lineal",
    text_angle: int = 0,
    color_mode: str = "Actual",
    color: str = "#808080",
    font_family: str = config.DEFAULT_FONT_FAMILY,
    logo_bytes: bytes | None = None,
    logo_scale: int = 25,
    logo_opacity: int = 128,
    logo_position: str = "center",
    stamp_text: str = "",
    stamp_position: str = "bottom-right",
) -> bytes:
    """Aplica la marca de agua y devuelve los bytes de un PNG."""
    image = Image.open(io.BytesIO(image_bytes))

    # Asegurar modo RGBA para poder componer la marca de agua.
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)
    font = _load_font(font_size, font_family)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Variables comunes
    spacing_x = text_width * 2  # Espaciado horizontal
    spacing_y = text_height * 2  # Espaciado vertical
    rows = int(image.height / spacing_y) + 2
    cols = int(image.width / spacing_x) + 2

    # Color del texto (RGB elegido) y alfa real controlado por la opacidad.
    r, g, b = _parse_hex(color)
    alpha = max(0, min(int(opacity), 255))
    text_fill = (r, g, b, alpha)

    if watermark_type == "Texto lineal":
        # Crear patrón lineal
        angle = text_angle
        txt_template = _text_tile(font, text, text_fill)
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

                txt = _text_tile(font, text, text_fill)
                txt = txt.rotate(angle, expand=True)

                paste_x = int(x_pos)
                paste_y = int(wave_y)
                if 0 <= paste_x < image.width and 0 <= paste_y < image.height:
                    image.paste(txt, (paste_x, paste_y), txt)

    # Logo opcional, en la posición elegida sobre el patrón de texto.
    if logo_bytes:
        try:
            _paste_logo(
                image,
                logo_bytes,
                scale=logo_scale,
                opacity=logo_opacity,
                position=logo_position,
            )
        except Exception as exc:  # noqa: BLE001 - un logo inválido no debe romper todo
            logger.warning("No se pudo componer el logo: %s", exc)

    # Sello opcional (p. ej. fecha) en la posición elegida. Se dibuja en su propio
    # tile (con `_text_tile`, que evita recortes) y se pega en la posición anclada.
    if stamp_text.strip():
        stamp_tile = _text_tile(font, stamp_text, text_fill)
        margin = max(8, int(image.width * 0.02))
        pos = _anchor(
            stamp_position,
            image.width,
            image.height,
            stamp_tile.width,
            stamp_tile.height,
            margin,
        )
        image.paste(stamp_tile, pos, stamp_tile)

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
