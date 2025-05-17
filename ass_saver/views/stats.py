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
                
                for row in range(-1, rows + 1):
                    for col in range(-1, cols + 1):
                        x = col * spacing_x
                        y = row * spacing_y
                        
                        # Alternar filas para crear patrón diagonal
                        if row % 2 == 0:
                            x += spacing_x / 2
                        
                        # Pegar solo si está dentro de los límites de la imagen
                        paste_x = int(x)
                        paste_y = int(y)
                        if (0 <= paste_x < image.width and 0 <= paste_y < image.height):
                            image.paste(txt_template, (paste_x, paste_y), txt_template)
                            
            elif self.watermark_type == "Texto ondulado":
                # Crear patrón ondulado
                spacing = text_height * 1.5
                frequency = 0.05
                amplitude = text_height * 0.5
                offset = -diagonal
                while offset < diagonal:
                    for i in range(-rows, rows):
                        base_x = offset + i * spacing
                        base_y = i * spacing
                        
                        # Aplicar efecto ondulado
                        wave_offset = amplitude * math.sin(frequency * base_x)
                        x = base_x
                        y = base_y + wave_offset
                        
                        # Calcular el ángulo de rotación basado en la onda
                        angle = math.degrees(math.atan(
                            amplitude * frequency * math.cos(frequency * base_x)
                        ))
                        
                        # Rotar el texto según el ángulo
                        txt = Image.new('RGBA', (int(text_width*1.5), int(text_height*1.5)), (255, 255, 255, 0))
                        d = ImageDraw.Draw(txt)
                        d.text((text_width/4, text_height/4), self.watermark_text, 
                              font=font, fill=(color_value, color_value, color_value, 255))
                        txt = txt.rotate(angle, expand=True)
                        
                        # Pegar solo si está dentro de los límites de la imagen
                        paste_x = int(x)
                        paste_y = int(y)
                        if (0 <= paste_x < image.width and 0 <= paste_y < image.height):
                            image.paste(txt, (paste_x, paste_y), txt)
                    
                    offset += spacing * 2
                    
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
            # Mostrar notificación de éxito
            yield rx.toast.success("¡Marca de agua aplicada con éxito!, solo necesitas descargarla para salvar tú culo!!")
            
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