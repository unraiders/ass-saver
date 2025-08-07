# Cambios en esta versión

## ⚠️ ¡Importante! CAMBIOS BLOQUEANTES.
Debemos eliminar los puertos expuestos actualmente y solo exponer uno. En este caso, el puerto 25501.

- 👷 Eliminados los puertos 3030 y 8030 expuestos actualmente.
- 👷 Añadido el puerto 25501.

## Cambios
- 🔧 Cambios en el Dockerfile para hacer el build en dos etapas, y cambiadas las imágenes base de python a alpine.
- 🔧 Actualizada la librería de Reflex (0.8.5) a su última versión.
- 🔧 Actualizada la librería de Pillow (11.3.0) a su última versión.
- 🔧 Cambios en la estética de la interfaz.

## Correcciones
- 🐛 Corregido el error de que no se podía aplicar la marca de agua a imágenes con un tamaño de archivo superior a 1 MB.
