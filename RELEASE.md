# Cambios en esta versión

## 🧹 Limpieza: eliminada la variable `DEBUG`

- **Retirada la variable de entorno `DEBUG`** de todo el proyecto (backend, `docker-compose`, plantilla de Unraid y documentación).
- El logger queda fijo en nivel `INFO`.
- Eliminado código muerto: `DEBUG` estaba definida en `config.py` pero no se usaba en ningún sitio.
