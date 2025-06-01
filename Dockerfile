FROM node:20-slim

LABEL maintainer="unraiders"
LABEL description="Inserta una marca de agua con tu texto en tus imágenes .png o .jpg para proteger tus documentos al realizar gestiones varias."

ARG VERSION=0.0.6
ENV VERSION=${VERSION}

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-full \
    curl \
    git \
    unzip \  
    build-essential \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crear y activar un entorno virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ass_saver/ ass_saver/
COPY assets/ assets/
COPY rxconfig.py .
COPY .web/_static .web/_static

EXPOSE 3000
EXPOSE 8000

CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0"]