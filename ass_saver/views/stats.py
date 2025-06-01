import reflex as rx
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import typing
import math

from reflex.style import set_color_mode

class State(rx.State):
    """El estado de la aplicación."""
    image: str = ""
    watermark_text: str = ""
    result_image: str = ""
    is_processing: bool = False
    error: str = ""
    font_size: int = 16  # Tamaño inicial de la fuente
    opacity: int = 125  # Valor inicial de opacidad (0-255)
    watermark_type: str = "Texto lineal"  # Tipo de disposición (lineal, ondulado, espiral)
    text_angle: int = 0  # Ángulo de rotación para texto lineal

    async def load_test_file(self):
        """Carga el archivo de prueba dni_ficticio.jpg."""
        try:
            with open("assets/dni_ficticio.jpg", "rb") as f:
                file_bytes = f.read()
            
            # Detectar el formato de la imagen
            image = Image.open(io.BytesIO(file_bytes))
            mime_type = Image.MIME[image.format]
            
            # Convertir bytes a base64
            img_str = base64.b64encode(file_bytes).decode()
            self.image = f"data:{mime_type};base64,{img_str}"
            
            self.result_image = ""
            self.error = ""
            yield rx.toast.success("Archivo de prueba cargado correctamente")
        except Exception as e:
            self.error = f"Error al cargar el archivo de prueba: {str(e)}"
            yield rx.toast.error("Error al cargar el archivo de prueba")

    def set_text_angle_from_string(self, value: str):
        """Actualiza el ángulo de rotación del texto desde un string con grados."""
        try:
            angle = int(value.replace("°", ""))
            self.text_angle = angle
        except ValueError:
            self.text_angle = 45  # valor por defecto si hay error

    def handle_upload(self, files: typing.Any):
        """Maneja la subida de archivos."""
        if not files:
            return
        
        try:
            file = files[0]
            # Convertir el objeto UploadFile a base64
            if hasattr(file, "read"):
                file_bytes = file.read()
            else:
                file_bytes = file
                
            # Detectar el formato de la imagen
            image = Image.open(io.BytesIO(file_bytes))
            mime_type = Image.MIME[image.format]
            
            # Convertir bytes a base64
            img_str = base64.b64encode(file_bytes).decode()
            self.image = f"data:{mime_type};base64,{img_str}"
                
            self.result_image = ""
            self.error = ""
            yield rx.toast.success("Archivo cargado correctamente")
        except Exception as e:
            self.error = f"Error al procesar el archivo: {str(e)}"
            yield rx.toast.error("Error al cargar el archivo de prueba")

    def set_font_size(self, size: list[int | float]):
        """Actualiza el tamaño de la fuente."""
        self.font_size = size[0]
        # Limpiar la imagen procesada para forzar reprocesamiento
        # self.result_image = ""

    def set_opacity(self, value: list[int | float]):
        """Actualiza la opacidad de la marca de agua."""
        self.opacity = int(value[0])
        # Limpiar la imagen procesada para forzar reprocesamiento
        # self.result_image = ""

    def set_watermark_type(self, value: str):
        """Actualiza el tipo de marca de agua."""
        self.watermark_type = value
        # Si cambiamos a un tipo que no es texto lineal, resetear el ángulo a 45
        if value != "Texto lineal":
            self.text_angle = 45
    
    def set_text_angle(self, value: int):
        """Actualiza el ángulo de rotación del texto."""
        self.text_angle = value
    
    def apply_watermark(self):
        """Aplica la marca de agua a la imagen."""
        if not self.image or not self.watermark_text:
            # self.error = "Por favor, sube una imagen y escribe un texto para la marca de agua."
            yield rx.toast.error("Por favor, sube una imagen y escribe un texto para la marca de agua.")
            return

        try:
            self.is_processing = True
            # Extraer los datos base64 de la URL de datos y procesar la imagen
            image_data = self.image.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Asegurar que la imagen esté en modo RGBA para la marca de agua
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            draw = ImageDraw.Draw(image)
            
            try:
                # Intentar cargar la fuente incluida en el proyecto
                import os
                font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
                font = ImageFont.truetype(font_path, int(self.font_size))
            except Exception as e:
                # Si falla, usar la fuente por defecto y mostrar el error
                yield rx.toast.error(f"Problemas para cargar la fuente: {str(e)}")
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Variables comunes
            spacing_x = text_width * 2  # Espaciado horizontal
            spacing_y = text_height * 2  # Espaciado vertical
            diagonal = math.sqrt(image.width**2 + image.height**2)
            rows = int(image.height / spacing_y) + 2
            cols = int(image.width / spacing_x) + 2
            color_value = 255 - self.opacity
            
            # Crear patrón según el tipo seleccionado
            if self.watermark_type == "Texto lineal":
                # Crear patrón lineal
                angle = self.text_angle
                txt_template = Image.new('RGBA', (int(text_width*1.5), int(text_height*1.5)), (255, 255, 255, 0))
                d = ImageDraw.Draw(txt_template)
                d.text((text_width/4, text_height/4), self.watermark_text, 
                      font=font, fill=(color_value, color_value, color_value, 255))
                txt_template = txt_template.rotate(angle, expand=True)
                
                # Ajustar el espaciado según el ángulo para evitar superposición
                adjusted_spacing_x = spacing_x
                adjusted_spacing_y = spacing_y
                
                # Para ángulos cercanos a 90º, ajustar el espaciado horizontal y vertical
                if abs(angle) % 180 > 75 and abs(angle) % 180 < 105:
                    # Cuando el texto está vertical o casi vertical, necesitamos más espaciado horizontal
                    adjusted_spacing_x = text_height * 2.5  # Reducir para texto vertical
                    adjusted_spacing_y = text_width * 1.2  # Usar ancho para espaciado vertical
                    rows = int(image.height / adjusted_spacing_y) + 4  # Más filas
                    cols = int(image.width / adjusted_spacing_x) + 4  # Más columnas
                
                # Calcular el área total a cubrir para asegurar que no queden espacios vacíos
                x_range = range(-2, cols + 3)  # Extender el rango para mejor cobertura
                y_range = range(-2, rows + 3)  # Extender el rango para mejor cobertura
                
                for row in y_range:
                    for col in x_range:
                        x = col * adjusted_spacing_x
                        y = row * adjusted_spacing_y
                        
                        # Alternar filas para crear patrón diagonal
                        if row % 2 == 0:
                            x += adjusted_spacing_x / 2
                        
                        # Pegar solo si está dentro de los límites de la imagen
                        paste_x = int(x)
                        paste_y = int(y)
                        if (0 <= paste_x < image.width and 0 <= paste_y < image.height):
                            image.paste(txt_template, (paste_x, paste_y), txt_template)
                            
            elif self.watermark_type == "Texto ondulado":
                # Crear verdadero patrón sinusoidal con textos siguiendo la onda
                
                # Parámetros para ondas más definidas y visibles
                wave_spacing_y = text_height * 8.0  # Gran espaciado vertical entre ondas
                frequency = 0.005  # Frecuencia controlada para ondas visibles pero no muy apretadas
                amplitude = text_height * 10.0  # Amplitud grande para ondas muy visibles
                
                # Calcular cantidad de ondas para cubrir la imagen
                num_waves = max(3, int(image.height / (wave_spacing_y + amplitude * 2))) + 1
                
                # Cálculo de espaciado horizontal basado en la frecuencia para evitar superposiciones
                # Queremos que haya aproximadamente un texto cada 30-40 grados de la onda
                period = 2 * math.pi / frequency  # Longitud de una onda completa en píxeles
                wave_spacing_x = period / 10  # 10 textos por onda completa
                
                # Crear ondas horizontales a través de la imagen
                for wave_idx in range(num_waves):
                    # Punto base de la onda - distribuido para cubrir toda la altura de la imagen
                    wave_y_base = wave_idx * wave_spacing_y + image.height / (num_waves * 1.5)
                    
                    # Fase alternada para líneas consecutivas - crea un efecto más natural
                    phase_offset = (wave_idx % 2) * math.pi
                    
                    # Número de textos a lo largo de la onda
                    num_texts = int(image.width / wave_spacing_x) + 8  # +8 para asegurar cobertura
                    
                    # Crear textos que sigan la forma sinusoidal
                    for i in range(-3, num_texts + 3):  # Extender fuera de los límites para mejor cobertura
                        x_pos = i * wave_spacing_x
                        
                        # Calcular posición Y siguiendo una onda sinusoidal perfecta
                        wave_y = wave_y_base + amplitude * math.sin(frequency * x_pos + phase_offset)
                        
                        # Calcular el ángulo tangente a la curva en este punto para rotar el texto
                        # La derivada de sin(ax) es a*cos(ax)
                        derivative = amplitude * frequency * math.cos(frequency * x_pos + phase_offset)
                        angle = math.degrees(math.atan(derivative))
                        
                        # Crear imagen con texto
                        txt = Image.new('RGBA', (int(text_width*1.5), int(text_height*1.5)), (255, 255, 255, 0))
                        d = ImageDraw.Draw(txt)
                        d.text((text_width/4, text_height/4), self.watermark_text, 
                              font=font, fill=(color_value, color_value, color_value, 255))
                        
                        # Rotar el texto para seguir la tangente a la curva en ese punto
                        txt = txt.rotate(angle, expand=True)
                        
                        # Pegar solo si está dentro de los límites de la imagen
                        paste_x = int(x_pos)
                        paste_y = int(wave_y)
                        
                        # Verificar que está dentro de los límites para evitar errores
                        if (0 <= paste_x < image.width and 0 <= paste_y < image.height):
                            image.paste(txt, (paste_x, paste_y), txt)
                    
            else:  # Texto espiral
                # Crear patrón en espiral
                center_x = image.width / 2
                center_y = image.height / 2
                spacing = text_height
                max_radius = math.sqrt((image.width/2)**2 + (image.height/2)**2)
                angle_step = 15
                radius_step = text_height * 0.5
                current_angle = 0
                current_radius = text_height
                
                while current_radius < max_radius:
                    x = center_x + current_radius * math.cos(math.radians(current_angle))
                    y = center_y + current_radius * math.sin(math.radians(current_angle))
                    
                    # Rotar el texto según el ángulo de la espiral
                    txt = Image.new('RGBA', (int(text_width*1.5), int(text_height*1.5)), (255, 255, 255, 0))
                    d = ImageDraw.Draw(txt)
                    d.text((text_width/4, text_height/4), self.watermark_text, 
                          font=font, fill=(color_value, color_value, color_value, 255))
                    rotation_angle = current_angle + 90
                    txt = txt.rotate(rotation_angle, expand=True)
                    
                    # Pegar solo si está dentro de los límites de la imagen
                    paste_x = int(x - text_width/2)
                    paste_y = int(y - text_height/2)
                    if (0 <= paste_x < image.width and 0 <= paste_y < image.height):
                        image.paste(txt, (paste_x, paste_y), txt)
                    
                    current_angle += angle_step
                    current_radius += radius_step / (2 * math.pi)
            
            # Crear un fondo blanco
            background = Image.new('RGB', image.size, (255, 255, 255))
            
            # Si la imagen tiene canal alfa, usar como máscara
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image)
            
            # Convertir a RGB y guardar como PNG
            if background.mode != 'RGB':
                background = background.convert('RGB')
            
            # Guardar la imagen
            buffered = io.BytesIO()
            background.save(buffered, format='PNG')
            buffered.seek(0)
            
            # Codificar en base64
            img_str = base64.b64encode(buffered.getvalue()).decode()
            self.result_image = f"data:image/png;base64,{img_str}"
            self.error = ""

            yield rx.toast.success("¡Marca de agua aplicada con éxito!, solo necesitas descargarla para salvar tú culo!!")
                
            yield rx.scroll_to("final")
            
        except Exception as e:
            self.error = f"Error al procesar la imagen: {str(e)}"
        finally:
            self.is_processing = False

    def reset_state(self):
        """Limpia el estado de la aplicación."""
        self.image = ""
        self.watermark_text = ""
        self.result_image = ""
        self.error = ""
        self.is_processing = False