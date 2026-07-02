# ASS-SAVER

Inserta una marca de agua con tu texto en tus imágenes `.png` o `.jpg` para proteger tus documentos al realizar gestiones varias.

Está especialmente indicado para poner una marca de agua en tu documento nacional de identidad (DNI) cuando, por alguna razón, tienes que enviarlo a terceros (altas, bajas, etc.) y quieres especificar el motivo de dicha gestión y que quede reflejado en el documento.

Como una de las posibles finalidades del archivo generado es el envío por email, al aplicar la marca de agua se realiza un redimensionado proporcional automático a 800px para reducir al máximo el tamaño del fichero.

> La aplicación no guarda ningún dato en local: todo el proceso se realiza en memoria. Solo se te permite descargar el documento una vez insertada la marca de agua.

## ¿Qué hace?

- **Vista previa en vivo**: el resultado se actualiza solo al cambiar cualquier ajuste.
- **Texto lineal** con **inclinación libre de 0° a 360°**.
- **Texto cruzado**: el texto sigue una onda para entrelazarse sobre la imagen.
- **Color del texto** personalizable y **opacidad** real (alfa) ajustable.
- **Fuente** seleccionable entre varias, agrupadas por estilo (sans serif, con serifa, monoespaciada e impacto). Por defecto **DejaVu Sans Mono**.
- **Modo de color**: Actual o Escala de grises.
- **Tamaño de fuente** ajustable.
- **Logo opcional** superpuesto, con tamaño, opacidad y posición configurables.
- **Sello de fecha** automático, con posición configurable.
- **Posición** del logo y del sello: cuatro esquinas o centro.
- **Redimensionado** proporcional automático a 800px de ancho.

## Stack

- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui.
- **Backend**: FastAPI (procesa la imagen con Pillow).
- **Empaquetado**: una única imagen Docker en la que el backend sirve tanto la API como la interfaz web compilada.

## Ejemplo `docker-compose.yml`

```yaml
services:
  ass-saver:
    image: unraiders/ass-saver:latest
    container_name: ass-saver
    ports:
      - "8000:8000"
    restart: unless-stopped
```

El puerto del contenedor es `8000` y puedes mapearlo libremente al puerto del host que prefieras (por ejemplo `9000:8000`).

## Instalación de la plantilla en Unraid

Descarga la plantilla a la carpeta de plantillas de usuario de Unraid:

```bash
wget -O /boot/config/plugins/dockerMan/templates-user/my-ass-saver.xml \
  https://raw.githubusercontent.com/unraiders/ass-saver/main/my-ass-saver.xml
```

Después, en Unraid, ve a **Docker → Add Container**, selecciona la plantilla `ass-saver` y ajusta el puerto si lo necesitas.

## Desarrollo

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

El frontend de desarrollo levanta en `http://localhost:3000` y hace proxy de `/api` al backend en `http://localhost:8000`.

## Uso

1. Sube una imagen (`.png` / `.jpg`) o pulsa **Cargar fichero de prueba**.
2. Escribe el texto de la marca de agua (por ejemplo: *SOLO VÁLIDO PARA DAR DE BAJA…*).
3. Ajusta tamaño de fuente, color, opacidad, fuente, modo de color y disposición (lineal o cruzado). En modo lineal puedes elegir la inclinación (0–360°).
4. Opcionalmente, añade un **logo** (con tamaño, opacidad y posición) y/o un **sello de fecha** en la esquina o centro que prefieras.
5. La **vista previa se actualiza automáticamente**; pulsa **Aplicar Marca de Agua** para forzar el procesado y descarga el resultado.
