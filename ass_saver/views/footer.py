import reflex as rx

from ass_saver.utils.config import VERSION


def footer() -> rx.Component:
    return rx.flex(
        rx.text(
            "ASS-SAVER - Desarrollado con",
            mt=6,
            font_size="12px",
            color="gray.500",
        ),
        rx.icon("heart", size=18, color="red"),
        rx.text(
            f"Versión {VERSION}",
            mt=6,
            font_size="12px",
            color="gray.500",
        ),
        spacing="2",
        position="sticky",
        bottom="0",
        id="final",       
    ) 