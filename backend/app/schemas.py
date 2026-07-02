"""Modelos Pydantic de request/response de la API."""
from pydantic import BaseModel, Field


class WatermarkRequest(BaseModel):
    """Petición para aplicar la marca de agua.

    `image` es una data-URL base64 (p. ej. `data:image/png;base64,...`) o el
    propio contenido base64 sin cabecera.
    """

    image: str = Field(..., description="Imagen en data-URL base64")
    text: str = Field(..., description="Texto de la marca de agua")
    font_size: int = 16
    opacity: int = 125
    watermark_type: str = "Texto lineal"
    text_angle: int = 0
    color_mode: str = "Actual"
    color: str = Field("#808080", description="Color del texto en hex")
    font_family: str = Field("DejaVu Sans", description="Nombre lógico de la fuente")
    logo: str = Field("", description="Logo opcional en data-URL base64")
    logo_scale: int = Field(25, description="Ancho del logo como % del ancho de la imagen")
    logo_opacity: int = Field(128, description="Alfa del logo (0-255)")
    logo_position: str = Field("center", description="Posición del logo (esquinas o centro)")
    stamp_text: str = Field("", description="Texto de sello (p. ej. fecha) o vacío")
    stamp_position: str = Field(
        "bottom-right", description="Posición del sello (esquinas o centro)"
    )


class WatermarkResponse(BaseModel):
    """Respuesta con la imagen resultante en data-URL base64."""

    success: bool
    image: str = ""
    message: str = ""
