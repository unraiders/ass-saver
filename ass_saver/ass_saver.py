import reflex as rx

from reflex.style import set_color_mode

from .views.navbar import navbar
from .views.stats import State


def index():
    return rx.center(
        rx.vstack(
            navbar(),           
            rx.hstack(
                rx.heading("La marca de agua en tus imágenes (png, jpg)", size="2"),
                rx.button(
                    "Limpiar",
                    on_click=State.reset_state,
                    color_scheme="brown",
                    size="1",
                ),
                width="100%",
                justify="between",
            ),
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.text(
                            "Arrastra una imagen aquí o haz clic para seleccionar",
                            size="1",
                            align="center",                            
                            ),
                        rx.button(
                            "Seleccionar Archivo", 
                            color_scheme="indigo",
                            radius="large",
                            align="center", 
                            ),
                            align="center", 
                    ),
                    border="2px dashed",
                    padding="4em",
                    border_radius="md",
                    on_drop=State.handle_upload,
                ),
                rx.badge(
                    "Cargar fichero de prueba",
                    on_click=State.load_test_file,
                    color_scheme="indigo",
                    variant="surface",
                    cursor="pointer",
                    margin_top="1em",
                ),
                align_items="center",
                width="100%",
            ),
            rx.cond(
                State.image,
                rx.vstack(
                    rx.image(src=State.image, max_width="400px", margin_y="1em"),
                    align="center",
                    width="100%",
                ),
            ),    

            rx.input(
                placeholder="Texto para la marca de agua",
                value=State.watermark_text,
                on_change=State.set_watermark_text,
                size="2",
                color_scheme="pink",                
                radius="large",
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                "Ejemplo: SOLO VÁLIDO PARA DAR DE BAJA MOVISTAR LA LIGA.",
                size="1",
                weight="light",
                color_scheme="cyan",
                color="gray.500",
                margin_top="-1em",
                margin_bottom="1em",
            ),
            rx.slider(
                default_value=16,
                min=10,
                max=100,
                step=2,
                on_change=State.set_font_size,
                color_scheme="pink",
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                f"Tamaño de fuente: {State.font_size}",
                margin_bottom="1em",
            ),
            rx.slider(
                default_value=125,
                min=0,
                max=255,
                step=5,
                on_change=State.set_opacity,
                color_scheme="pink",
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                f"Opacidad: {State.opacity}",
                margin_bottom="1em",
            ),
            
            # Añadir los radio groups aquí
            rx.vstack(
                rx.text("Tipo de disposición de la marca de agua:", margin_bottom="0.5em"),
                rx.radio_group(
                    [
                        "Texto lineal",
                        "Texto ondulado",
                        "Texto espiral",
                    ],
                    value=State.watermark_type,
                    on_change=State.set_watermark_type,
                    color_scheme="pink",
                ),
                align_items="start",
                margin_y="1em",
                width="100%",
            ),
            
            # Radio group para el ángulo (deshabilitado si no es texto lineal)
            rx.vstack(
                rx.text("Inclinación del texto:", margin_bottom="0.5em"),
                rx.radio_group(
                    [
                        "0°",
                        "45°",
                        "90°",
                        "180°",
                    ],
                    value=f"{State.text_angle}°",
                    on_change=State.set_text_angle_from_string,
                    color_scheme="pink",
                    is_disabled=rx.cond(
                        State.watermark_type == "Texto lineal",
                        False,
                        True,
                    ),
                    opacity=rx.cond(
                        State.watermark_type == "Texto lineal",
                        "1",
                        "0.5",
                    ),
                ),
                align_items="start",
                margin_y="1em",
                width="100%",
            ),
            
            rx.button(
                "Aplicar Marca de Agua",
                on_click=State.apply_watermark,
                is_loading=State.is_processing,
                color_scheme="indigo",
                width="100%",
                radius="large",
            ),
            rx.cond(
                State.error,
                rx.text(State.error, color="red"),
            ),
            rx.cond(
                State.result_image,
                rx.vstack(
                    rx.image(src=State.result_image, max_width="400px", margin_y="1em", align="center"),
                    rx.button(
                        "Descargar Imagen",
                        color_scheme="green",
                        width="100%",
                        on_click=rx.download(url=State.result_image, filename="save-your-ass_watermarked.png"),
                    ),
                    align="center",
                    width="100%",
                ),
            ),
            width="100%",
            max_width="500px",
            spacing="4",
            padding="2em",
            id="result",
        ),
        align="center",
    )

app = rx.App()
app.add_page(index)
