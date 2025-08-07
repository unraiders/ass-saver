# Etapa de build
FROM alpine:3.21.3 AS builder

ARG VERSION=0.1.0
ARG PORT=25501
ARG API_URL

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    bash \
    nodejs \
    npm \
    git \
    build-base

WORKDIR /app

COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY rxconfig.py ./
RUN reflex init

COPY . .

RUN REFLEX_API_URL=${API_URL:-http://localhost:$PORT} reflex export --loglevel debug --frontend-only --no-zip \
    && mv .web/build/client/* /srv/ \
    && rm -rf .web

# Etapa final
FROM alpine:3.21.3

ARG VERSION
ARG PORT=25501
ARG API_URL

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    caddy 

WORKDIR /app

COPY Caddyfile .
COPY rxconfig.py .
COPY entrypoint.sh .
COPY ass_saver ./ass_saver
COPY assets ./assets

COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

ENV PORT=$PORT
ENV REFLEX_API_URL=${API_URL:-http://localhost:$PORT}
ENV PYTHONUNBUFFERED=1
ENV VERSION=${VERSION}

COPY --from=builder /srv /srv

STOPSIGNAL SIGKILL

EXPOSE $PORT

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]