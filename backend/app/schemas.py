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


class WatermarkResponse(BaseModel):
    """Respuesta con la imagen resultante en data-URL base64."""

    success: bool
    image: str = ""
    message: str = ""
