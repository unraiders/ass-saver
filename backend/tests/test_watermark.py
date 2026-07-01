"""Pruebas de la lógica de marca de agua."""
import io

from PIL import Image

from app.core.watermark import apply_watermark


def _sample_image(width: int = 1200, height: int = 900) -> bytes:
    """Genera un JPEG de prueba en memoria."""
    img = Image.new("RGB", (width, height), (120, 140, 160))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_devuelve_png_valido():
    out = apply_watermark(_sample_image(), text="PRUEBA")
    assert out[:8] == b"\x89PNG\r\n\x1a\n"  # cabecera PNG


def test_redimensiona_a_800():
    out = apply_watermark(_sample_image(1600, 1200), text="PRUEBA")
    img = Image.open(io.BytesIO(out))
    assert img.width == 800
    # Mantiene la proporción original (4:3).
    assert img.height == 600


def test_no_agranda_imagen_pequena():
    out = apply_watermark(_sample_image(400, 300), text="PRUEBA")
    img = Image.open(io.BytesIO(out))
    assert img.width == 400


def test_escala_de_grises():
    out = apply_watermark(
        _sample_image(300, 300), text="PRUEBA", color_mode="Escala de grises"
    )
    img = Image.open(io.BytesIO(out)).convert("RGB")
    # En escala de grises los tres canales coinciden.
    r, g, b = img.getpixel((10, 10))
    assert r == g == b


def test_texto_cruzado():
    out = apply_watermark(
        _sample_image(500, 500), text="PRUEBA", watermark_type="Texto cruzado"
    )
    assert out[:8] == b"\x89PNG\r\n\x1a\n"
