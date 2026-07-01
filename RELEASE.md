# Cambios en esta versión

## 🚀 Primera versión con el nuevo stack

- **Reescritura completa** de la aplicación: frontend en React + Vite + TypeScript + Tailwind + shadcn/ui y backend en FastAPI.
- **Una sola imagen Docker**: el backend sirve tanto la API como la interfaz web compilada.
- **Publicación en DockerHub y GHCR** con builds automatizados.
- **Puerto configurable** (por defecto 8000), mapeable libremente al host.
- Se mantiene toda la funcionalidad de marca de agua: texto lineal (0°, 45°, 90°, 180°), texto cruzado, escala de grises, opacidad y tamaño de fuente ajustables, con redimensionado proporcional a 800px.
