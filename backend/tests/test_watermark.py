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


def _png_image(bytes_: bytes) -> Image.Image:
    return Image.open(io.BytesIO(bytes_)).convert("RGB")


def test_color_personalizado_aparece_en_la_imagen():
    # Texto rojo puro y opaco sobre un fondo gris: debe aparecer algún píxel rojizo.
    out = apply_watermark(
        _sample_image(400, 400),
        text="XXXXXX",
        font_size=40,
        opacity=255,
        color="#ff0000",
    )
    img = _png_image(out)
    pixels = list(img.getdata())
    # Algún píxel claramente rojo (R alto, G y B bajos).
    assert any(r > 180 and g < 80 and b < 80 for r, g, b in pixels)


def test_angulo_arbitrario():
    out = apply_watermark(_sample_image(500, 500), text="PRUEBA", text_angle=30)
    assert out[:8] == b"\x89PNG\r\n\x1a\n"


def test_fuente_invalida_cae_a_defecto():
    # Una fuente desconocida no debe provocar error: usa la de por defecto.
    out = apply_watermark(
        _sample_image(300, 300), text="PRUEBA", font_family="Fuente Inexistente"
    )
    assert out[:8] == b"\x89PNG\r\n\x1a\n"


def test_fuente_valida_alternativa():
    out = apply_watermark(
        _sample_image(300, 300), text="PRUEBA", font_family="DejaVu Serif"
    )
    assert out[:8] == b"\x89PNG\r\n\x1a\n"


def test_logo_compuesto():
    # Logo rojo semitransparente: la imagen resultante sigue siendo un PNG válido
    # con el redimensionado esperado.
    logo = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
    buf = io.BytesIO()
    logo.save(buf, format="PNG")
    out = apply_watermark(
        _sample_image(1600, 1200),
        text="PRUEBA",
        logo_bytes=buf.getvalue(),
        logo_scale=30,
        logo_opacity=200,
    )
    img = _png_image(out)
    assert img.width == 800


def test_sello_de_fecha():
    out = apply_watermark(
        _sample_image(500, 500), text="PRUEBA", stamp_text="02/07/2026"
    )
    assert out[:8] == b"\x89PNG\r\n\x1a\n"


def test_logo_en_esquina():
    # Logo rojo opaco en la esquina superior izquierda: esa zona debe ser roja.
    logo = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
    buf = io.BytesIO()
    logo.save(buf, format="PNG")
    out = apply_watermark(
        _sample_image(800, 800),
        text="X",
        logo_bytes=buf.getvalue(),
        logo_scale=25,
        logo_opacity=255,
        logo_position="top-left",
    )
    img = _png_image(out)
    # Muestreo cerca de la esquina superior izquierda (tras redimensionado).
    r, g, b = img.getpixel((30, 30))
    assert r > 180 and g < 80 and b < 80
    # La esquina opuesta NO debe ser roja.
    r2, g2, b2 = img.getpixel((img.width - 30, img.height - 30))
    assert not (r2 > 180 and g2 < 80 and b2 < 80)


def test_sello_en_posicion():
    out = apply_watermark(
        _sample_image(500, 500),
        text="PRUEBA",
        stamp_text="02/07/2026",
        stamp_position="top-left",
    )
    assert out[:8] == b"\x89PNG\r\n\x1a\n"
