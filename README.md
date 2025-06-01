# ASS-SAVER

Inserta una marca de agua con tu texto en tus imágenes .png o .jpg para proteger tus documentos al realizar gestiones varias.

Está especialmente indicado para poner una marca de agua en nuestro documento nacional de identidad (DNI), cuando por alguna razón tenemos que enviarlo a terceros (altas, bajas, etc.) y queremos especificar el motivo de dicha gestión y que quede reflejado en el documento. 

## Versión inicial en desarrollo.

Este proyecto está en fase experimental pero funcional parcialmente, posiblemente con la funcionalidad de texto lineal ya sea suficiente para un uso general y posiblemente no tengas más versiones ni cambios en el código.

Que funciona:

-  Texto lineal en inclinación de 0º, 45º, 90º, 180º.

Que no funciona:

- Texto ondulado: El texto ondulado a pesar de no ser ondulado igual podría servir en determinadas ocasiones de texto que se pueda entrelazar.

- Texto espiral: Totalmente ilegible.

La aplicación no guarda ningún dato en local, todo el proceso se realiza en memoria, lo que si nos permite es descargar el documento una vez insertada la marca de agua.

Este mini proyecto está realizado con el framework Reflex de Python, este framework por su envergadura igual no sería el idóneo para este proyecto de prueba tan simple, por lo que quiere decir que al levantar el contenedor necesita un tiempo en levantar todos los servicios, dale su tiempo... siéntete libre de descargarlo y modificarlo a tú gusto o simplemente para hacer pruebas. 

Este proyecto tiene una parte frontend y una parte backend, por eso en el docker compose se exponen dos puertos, en este caso el frontend en el 3030 y el backend en el 8030.

```
services:
  ass-saver:
    image: unraiders/ass-saver
    container_name: ass-saver
    ports:
      - 3030:3030
      - 8030:8030
    network_mode: bridge
    restart: unless-stopped
```
Si quieres exponer el contenedor para que sea accesible desde el exterior de tu red, en el caso de NPM (Nginx Proxy Manager) a la hora de crear el registro del Proxy Host hay que hacer uso de Custom Locations, en este caso crearemos uno, quedando así:

```
Define location:
location: /_event
Scheme: http
Forward Hostname / IP: La IP dónde está instalado el contenedor.
Forward Port: 8030
En el campo de texto escribir lo siguiente:
location /_event {
     proxy_pass http://<ip_contenedor>:8030;
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
}
```
---

Demo: [https://ass-saver.marcallao.com](https://ass-saver.marcallao.com)

---


