# ASS-SAVER

Inserta una marca de agua con tu texto en tus imágenes .png o .jpg para proteger tus documentos al realizar gestiones varias.

Está especialmente indicado para poner una marca de agua en nuestro documento nacional de identidad (DNI), cuando por alguna razón tenemos que enviarlo a terceros (altas, bajas, etc.) y queremos especificar el motivo de dicha gestión y que quede reflejado en el documento. 

## Versión inicial.

Este proyecto está en fase experimental pero funcional, posiblemente con la funcionalidad de texto lineal ya sea suficiente para un uso general y posiblemente no tengas más versiones ni cambios en el código.

Que funciona:

- Texto lineal en inclinación de 0º, 45º, 90º, 180º.

- Opción de Modo de color: Actual o Escala de grises. 

- Texto cruzado: El texto cruzado podría servir en determinadas ocasiones para texto que se pueda entrelazar.

La aplicación no guarda ningún dato en local, todo el proceso se realiza en memoria, lo que si nos permite es descargar el documento una vez insertada la marca de agua.

---

Este miniproyecto está realizado con el framework Reflex de Python, este framework por su envergadura igual no sería el idóneo para este tipo de proyectos de prueba tan simple, es un framework de Python mas enfocado en tener el frontend y el backend separados, por lo que quiere decir que, al levantar el contenedor todo en local y tener que compilar el frontend necesitará tener los puertos definidos para su comunicación con el backend, en este caso el puerto 25501 quedará asignado, si en algún momento Reflex permite cambiar el puerto host del contenedor después de la generación de la imagen Docker cambiaré el código para admitir esa característica.
 
---

  > [!IMPORTANT]
  > Dado que la exportación del frontend se realiza en la compilación de la imagen de momento no podemos cambiar el puerto host y siempre tendrá que trabajar en el 25501 para que funcione el backend instalado en la misma imagen, o sea, no cambiar la asignación de los puertos de 25501:25501.

---

```
services:
  ass-saver:
    image: unraiders/ass-saver
    container_name: ass-saver
    ports:
      - 25501:25501
    network_mode: bridge
    restart: unless-stopped
```
Si quieres exponer el contenedor para que sea accesible desde el exterior de tu red, en el caso de NPM (Nginx Proxy Manager) a la hora de crear el registro del Proxy Host hay que hacer uso de Custom Locations, en este caso crearemos uno, quedando así:

```
Define location:
location: /_event
Scheme: http
Forward Hostname / IP: La IP dónde está instalado el contenedor.
Forward Port: 25501
En el campo de texto escribir lo siguiente:
location /_event {
     proxy_pass http://<ip_contenedor>:25501;
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
}
```
---

Demo: [https://ass-saver.marcallao.com](https://ass-saver.marcallao.com)

---


