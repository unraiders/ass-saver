import reflex as rx
import os
import re
from pathlib import Path


def get_version():
    # Primero intenta obtener la versión desde las variables de entorno
    version = os.environ.get("VERSION")
    
    # Si no está disponible en las variables de entorno, lee el Dockerfile
    if not version:
        try:
            dockerfile_path = Path(__file__).parents[2] / "Dockerfile"
            if dockerfile_path.exists():
                with open(dockerfile_path, "r") as f:
                    content = f.read()
                    # Busca la línea ARG VERSION=x.x.x
                    version_match = re.search(r'ARG VERSION=([0-9.]+)', content)
                    if version_match:
                        version = version_match.group(1)
        except Exception:
            pass
    
    return version or "N/A"


def footer():
    version = get_version()
    
    return rx.box(
        rx.hstack(
            rx.image(src="/logo.png", width="18px", height="auto"),
            rx.text(f"v{version}", font_size="12px", color="gray.500", margin_left="3px"),
            spacing="1",
            align_items="center",
        ),
        position="sticky",
        bottom="0",
        id="final",
    )