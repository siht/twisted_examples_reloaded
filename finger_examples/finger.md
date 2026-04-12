# el ejemplo de finger

## que es finger
es un servicio que da la información de un usuario en un sistema. Si ejecutabas ```finger nail``` o ```finger nail@example.com``` te devolvía información de usuario nail. Algo como esto:

```
Login: nail                           Name: Nail Sharp
Directory: /home/nail                 Shell: /usr/bin/sh
Last login Wed Mar 31 18:32 2004 (PST)
New mail received Thu Apr  1 10:50 2004 (PST)
     Unread since Thu Apr  1 10:50 2004 (PST)
No Plan.
```
## instrucciones

En este commit vamos a hacer que el reactor haga algo, anteriormente descartaba las conexiones porque no había algo que la gestione, pero ahora pondremos un protocolo, pero para que se pueda usar un protocolo necesitamos una factory, este protocolo hace absolutamente... nada, bueno como mínimo no descarta las conexiones.

también fijate que en la versión deferred puse una función main que hace que se vea mas similar a la versión con async/await

por cierto en el commit anterior se me olvidó que debías probar el código con un cliente que pueda comunicarse en este caso usaremos telnet, sin embargo como en el anteriro ejemplo no había ningún puerto escuchando tampoco había mucho caso, no habí un punto de entrada pero ahora ya

así que para poner nuestros servidores en acción (toma en cuenta que ambos escuchan el mismo puerto así que no es posible poner a funcionar ambos a menos que le cambies a uno el puerto):

```shell
python finger.py
```

o

```shell
python async_finger.py
```


para probar el resultado

```shell
telnet 127.0.0.1 1079
```

se conectará pero no hab´ra ningun resultado en pantalla puesto que el protocolo hace absolutamente nada.

