# ---------- Stage 1: build del frontend (Vite) ----------
FROM node:22-alpine AS frontend-build

WORKDIR /frontend

# La versión real la inyecta el workflow vía --build-arg desde .version_main / .version_develop.
# "local" es el valor por defecto para builds manuales sin --build-arg.
ARG VERSION=local
ENV VITE_APP_VERSION=${VERSION}

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: runtime (FastAPI) ----------
FROM python:3.13-slim AS runtime

LABEL maintainer="unraiders"
LABEL description="Inserta una marca de agua con tu texto en tus imágenes .png o .jpg para proteger tus documentos al realizar gestiones varias."
# Vincula la imagen de GHCR con el repositorio (pestaña Packages del repo).
LABEL org.opencontainers.image.source="https://github.com/unraiders/ass-saver"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    STATIC_DIR=/app/app/static \
    FONT_PATH=/app/app/assets/fonts/DejaVuSans.ttf

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Código del backend (incluye la fuente en app/assets/fonts)
COPY backend/app ./app

# Estáticos del frontend compilado
COPY --from=frontend-build /frontend/dist ./app/static

# La versión real la inyecta el workflow vía --build-arg; "local" por defecto.
ARG VERSION=local
ENV VERSION=${VERSION}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
