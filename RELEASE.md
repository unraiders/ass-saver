# Cambios en esta versión

## ✨ Más opciones de personalización de la marca de agua

- **Vista previa en vivo**: la marca se reaplica automáticamente (con un pequeño retardo) al cambiar cualquier parámetro; ya no hace falta pulsar *Aplicar* tras cada ajuste.
- **Color personalizable** del texto mediante selector de color. Ahora la **opacidad es alfa real** (antes solo controlaba el tono de gris).
- **Inclinación libre 0–360°** con un deslizador (antes solo 0/45/90/180°).
- **Selección de fuente** con desplegable agrupado por estilo. Nuevas fuentes incluidas (licencias OFL/Apache):
  - *Sans serif*: DejaVu Sans, Open Sans, Montserrat.
  - *Con serifa*: DejaVu Serif, PT Serif.
  - *Monoespaciada*: DejaVu Sans Mono (**por defecto**).
  - *Impacto*: DejaVu Sans Bold, Oswald, Anton.
- **Logo opcional** superpuesto: sube una imagen y ajusta su tamaño, opacidad y posición.
- **Sello de fecha** automático: marca la casilla para estampar la fecha de hoy.
- **Posición configurable** para el logo y para el sello: cuatro esquinas o centro.

## 🐛 Correcciones

- Solucionado el recorte del texto por su parte inferior con determinadas fuentes: cada instancia del texto (y el sello) se dibuja ahora en un lienzo ajustado a su bounding box real, evitando cortes en ascendentes y descendentes.
