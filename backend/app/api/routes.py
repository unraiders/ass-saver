"""Endpoints de la API bajo el prefijo /api."""
import base64
import binascii

from fastapi import APIRouter

from app.core.watermark import apply_watermark
from app.logging_config import setup_logger
from app.schemas import WatermarkRequest, WatermarkResponse

logger = setup_logger(__name__)

router = APIRouter(prefix="/api")


def _decode_image(data: str) -> bytes:
    """Extrae los bytes de una data-URL base64 o de base64 puro."""
    if "," in data:
        data = data.split(",", 1)[1]
    return base64.b64decode(data)


@router.post("/watermark", response_model=WatermarkResponse)
def watermark(req: WatermarkRequest) -> WatermarkResponse:
    """Aplica la marca de agua y devuelve la imagen como data-URL PNG."""
    if not req.image or not req.text.strip():
        return WatermarkResponse(
            success=False,
            message="Por favor, sube una imagen y escribe un texto para la marca de agua.",
        )

    try:
        image_bytes = _decode_image(req.image)
    except (binascii.Error, ValueError):
        return WatermarkResponse(success=False, message="La imagen recibida no es válida.")

    try:
        result_bytes = apply_watermark(
            image_bytes,
            text=req.text,
            font_size=req.font_size,
            opacity=req.opacity,
            watermark_type=req.watermark_type,
            text_angle=req.text_angle,
            color_mode=req.color_mode,
        )
    except Exception as exc:  # noqa: BLE001 - se reporta al cliente
        logger.exception("Error al procesar la imagen")
        return WatermarkResponse(
            success=False, message=f"Error al procesar la imagen: {exc}"
        )

    encoded = base64.b64encode(result_bytes).decode()
    return WatermarkResponse(
        success=True,
        image=f"data:image/png;base64,{encoded}",
        message="¡Marca de agua aplicada con éxito!",
    )
