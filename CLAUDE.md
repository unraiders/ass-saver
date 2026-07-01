# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

ASS-SAVER inserta una marca de agua de texto sobre imágenes `.png`/`.jpg` para proteger documentos (p. ej. el DNI) antes de enviarlos a terceros. Todo el procesado ocurre en memoria; no se persiste ningún dato ni fichero.

## Arquitectura

Monorepo con dos partes que se empaquetan en **una sola imagen Docker**: el backend FastAPI sirve tanto la API como el frontend ya compilado.

- **`backend/`** — FastAPI + Pillow.
  - `app/main.py`: monta el router `/api` y, si `STATIC_DIR` existe, sirve el SPA (mount de `/assets` y catch-all `/{full_path}` que devuelve el fichero estático o `index.html`).
  - `app/api/routes.py`: único endpoint real `POST /api/watermark`. Decodifica la imagen (data-URL base64 o base64 puro), llama a `apply_watermark` y devuelve la imagen resultante como data-URL PNG. Además hay `GET /api/health`.
  - `app/core/watermark.py`: **toda la lógica de imagen**. `apply_watermark()` soporta dos disposiciones: `"Texto lineal"` (rejilla rotada al ángulo dado) y `"Texto cruzado"` (los textos siguen una onda sinusoidal, rotando cada instancia según la tangente). Siempre aplana sobre fondo blanco, opcionalmente convierte a escala de grises y **redimensiona a 800px de ancho** (`TARGET_WIDTH`) manteniendo proporción, sin agrandar imágenes más pequeñas. Devuelve bytes PNG.
  - `app/schemas.py`: `WatermarkRequest`/`WatermarkResponse` (Pydantic). Los valores por defecto de los parámetros de marca de agua viven aquí.
  - `app/config.py`: configuración por variables de entorno (`VERSION`, `STATIC_DIR`, `FONT_PATH`). La fuente incluida es `app/assets/fonts/DejaVuSans.ttf`.

- **`frontend/`** — React + Vite + TypeScript + Tailwind + shadcn/ui.
  - `src/store/useAppStore.ts`: estado global con Zustand.
  - `src/api/client.ts`: cliente `fetch` contra `/api/*` (mismo origen en producción; en dev, proxy de Vite).
  - `src/components/WatermarkForm.tsx`: formulario principal; `src/components/ui/` son primitivos shadcn.

### Flujo de datos

Imagen → el frontend la lee como **data-URL base64** → `POST /api/watermark` con los parámetros → Pillow procesa en memoria → respuesta con la imagen resultante en data-URL PNG que el usuario descarga. No hay filesystem ni base de datos.

Los valores de `watermark_type`, `color_mode` y `text_angle` son **strings/ints acordados entre frontend y backend** (p. ej. `"Texto lineal"`, `"Escala de grises"`). Si cambias uno, cámbialo en ambos lados y en el `switch` de `watermark.py`.

## Comandos de desarrollo

**Backend** (desde `backend/`):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest                    # todos los tests
pytest tests/test_watermark.py::test_redimensiona_a_800   # un solo test
```
Los tests (`backend/tests/test_watermark.py`) prueban directamente `apply_watermark` con imágenes generadas en memoria; no requieren servidor. No hay `pytest.ini`/`pyproject.toml`: ejecuta `pytest` desde `backend/` para que `import app...` resuelva.

**Frontend** (desde `frontend/`):
```bash
npm install
npm run dev       # Vite en localhost:3000, proxya /api a localhost:8000
npm run build     # tsc --noEmit + vite build → dist/
```
En dev necesitas backend y frontend corriendo a la vez (el frontend proxya `/api`). En producción solo corre el backend, que sirve `dist/` desde `STATIC_DIR`.

**Docker** (imagen combinada):
```bash
docker compose -f docker-compose_local.yml up --build   # build local
```
El `Dockerfile` es multi-stage: stage `frontend-build` (node:22-alpine) compila el SPA, stage `runtime` (python:3.13-slim) instala el backend y copia `frontend/dist` en `app/static`. `docker-compose.yml` usa la imagen publicada de DockerHub; `docker-compose_local.yml` construye en local. Puerto del contenedor: `8000`.

## Versionado y despliegue

La versión vive en `.version_main` (rama `main` → tag `latest`) y `.version_develop` (rama `develop` → tag `develop`, prerelease). El workflow `.github/workflows/despliegue.yml` se dispara al hacer push a esas ramas: lee el fichero de versión de la rama, la inyecta como `--build-arg VERSION`, publica en DockerHub + GHCR y crea el Release usando `RELEASE.md` como notas. Actualiza `RELEASE.md` con los cambios de la versión antes de desplegar. Existe el skill `/despliega` para preparar una release.
