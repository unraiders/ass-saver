import reflex as rx

from reflex.style import set_color_mode

from ass_saver.views.navbar import navbar
from ass_saver.views.footer import footer    
from ass_saver.state.MainState import MainState


def scroll_to_bottom():
    return rx.call_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")

def index():
    return rx.center(
        rx.vstack(
            navbar(),           
            rx.hstack(
                rx.heading("La marca de agua en tus imágenes (png, jpg)", size="2"),
                rx.button(
                    "Limpiar",
                    on_click=MainState.reset_state,
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
                            align="center", 
                            ),
                            align="center", 
                    ),
                    border="2px dashed",
                    padding="4em",
                    border_radius="md",
                    id="upload1",
                    on_drop=MainState.handle_upload(
                        rx.upload_files(upload_id="upload1")
                    ),
                    multiple=False,
                    accept={
                        "image/png": [".png"],
                        "image/jpeg": [".jpg", ".jpeg"],
                    },
                ),
                rx.badge(
                    "Cargar fichero de prueba",
                    on_click=MainState.load_test_file,
                    variant="surface",
                    cursor="pointer",
                    margin_top="1em",
                ),
                align_items="center",
                width="100%",
            ),
            rx.cond(
                MainState.image,
                rx.vstack(
                    rx.image(src=MainState.image, max_width="400px", margin_y="1em"),
                    align="center",
                    width="100%",
                ),
            ),    

            rx.input(
                placeholder="Texto para la marca de agua",
                value=MainState.watermark_text,
                on_change=MainState.set_watermark_text,
                size="2",
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                "Ejemplo: SOLO VÁLIDO PARA DAR DE BAJA MOVISTAR LA LIGA.",
                size="1",
                weight="light",
                color_scheme="brown",
                color="gray.500",
                margin_top="-1em",
                margin_bottom="1em",
            ),
            rx.slider(
                default_value=16,
                min=10,
                max=100,
                step=2,
                on_change=MainState.set_font_size,
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                f"Tamaño de fuente: {MainState.font_size}",
                margin_bottom="1em",
            ),
            rx.slider(
                default_value=125,
                min=0,
                max=255,
                step=5,
                on_change=MainState.set_opacity,
                margin_y="1em",
                width="100%",
            ),
            rx.text(
                f"Opacidad: {MainState.opacity}",
                margin_bottom="1em",
            ),
            
            # Radio group para el modo de color
            rx.vstack(
                rx.text("Modo de color:", margin_bottom="0.5em"),
                rx.radio_group(
                    [
                        "Actual",
                        "Escala de grises",
                    ],
                    value=MainState.color_mode,
                    on_change=MainState.set_color_mode,
                ),
                align_items="start",
                margin_y="1em",
                width="100%",
            ),
            
            # Añadir los radio groups aquí
            rx.vstack(
                rx.text("Tipo de disposición de la marca de agua:", margin_bottom="0.5em"),
                rx.radio_group(
                    [
                        "Texto lineal",
                        "Texto cruzado",
                    ],
                    value=MainState.watermark_type,
                    on_change=MainState.set_watermark_type,
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
                    value=f"{MainState.text_angle}°",
                    on_change=MainState.set_text_angle_from_string,
                    is_disabled=rx.cond(
                        MainState.watermark_type == "Texto lineal",
                        False,
                        True,
                    ),
                    opacity=rx.cond(
                        MainState.watermark_type == "Texto lineal",
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
                on_click=MainState.apply_watermark,
                is_loading=MainState.is_processing,
                width="100%",
            ),
            
            rx.cond(
                MainState.error,
                rx.text(MainState.error, color="red"),
            ),
            rx.cond(
                MainState.result_image,
                rx.vstack(
                    rx.image(src=MainState.result_image, max_width="400px", margin_y="1em", align="center"),
                    rx.button(
                        "Descargar Imagen",
                        width="100%",
                        on_click=rx.download(url=MainState.result_image, filename="save-your-ass_watermarked.png"),
                    ),
                    align="center",
                    width="100%",
                ),
            ),
            rx.center(
                footer(),
                width="100%"
            ),
            width="100%",
            max_width="500px",
            spacing="4",
            padding="2em",
            id="result",
        ),
    ),

app = rx.App(
    theme=rx.theme(
        accent_color="brown", 
        gray_color="slate", 
        appearance="dark", 
        radius="full"
    )
)
app.add_page(index)
