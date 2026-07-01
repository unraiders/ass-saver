"""Punto de entrada FastAPI: monta la API y sirve el frontend compilado."""
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.api.routes import router

app = FastAPI(title="ASS-SAVER", version=config.VERSION)
app.include_router(router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": config.VERSION}


# Servir el frontend compilado (Vite build) como SPA.
# En desarrollo el frontend corre con `npm run dev` y proxya /api,
# por lo que STATIC_DIR puede no existir todavía.
if os.path.isdir(config.STATIC_DIR):
    assets_dir = os.path.join(config.STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Devuelve archivos estáticos o index.html para rutas del SPA."""
        candidate = os.path.join(config.STATIC_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(config.STATIC_DIR, "index.html"))
