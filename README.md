# ASS-SAVER

Inserta una marca de agua con tu texto en tus imágenes `.png` o `.jpg` para proteger tus documentos al realizar gestiones varias.

Está especialmente indicado para poner una marca de agua en tu documento nacional de identidad (DNI) cuando, por alguna razón, tienes que enviarlo a terceros (altas, bajas, etc.) y quieres especificar el motivo de dicha gestión y que quede reflejado en el documento.

Como una de las posibles finalidades del archivo generado es el envío por email, al aplicar la marca de agua se realiza un redimensionado proporcional automático a 800px para reducir al máximo el tamaño del fichero.

> La aplicación no guarda ningún dato en local: todo el proceso se realiza en memoria. Solo se te permite descargar el documento una vez insertada la marca de agua.

## ¿Qué hace?

- **Texto lineal** con inclinación de 0°, 45°, 90° o 180°.
- **Texto cruzado**: el texto sigue una onda para entrelazarse sobre la imagen.
- **Modo de color**: Actual o Escala de grises.
- **Opacidad** y **tamaño de fuente** ajustables.
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
3. Ajusta tamaño de fuente, opacidad, modo de color y disposición (lineal o cruzado). En modo lineal puedes elegir la inclinación.
4. Pulsa **Aplicar Marca de Agua** y descarga el resultado.
