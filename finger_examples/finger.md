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

Ahora hemos cambiado un poco la estructura ya que vamos a llamar las aplicaciones con twistd, pero como vamos a usar puertos privilegiados necesitamos permisos de adminitrador.

En mi caso usé conda y para encontrar el binario de twistd para poder ejecutar lo usé ```whereis twistd```, ya que si ejecuto:

```sh
sudo twistd -ny finger.tac
```

este no se va a encontrar en el path del root, así que lo más afácil y sencillo para mi es usar la ruta completa que me va a dar whereis o sea:

```sh
sudo /una/ruta/hiperlarga/donde/estan/los/envs/de/conda/twistd -ny finger.tac
```

así que para poner nuestros servidores en acción (toma en cuenta que ambos escuchan el mismo puerto así que no es posible poner a funcionar ambos a menos que le cambies a uno el puerto):

```shell
sudo twistd -ny finger.py
```

o

```shell
sudo twistd -ny async_finger.py
```


para probar el resultado

```shell
telnet 127.0.0.1 79 # para ver los usuarios
```

y en un navegador entrar a localhost:8000/<usuario>

y en el irc mandale un mensaje privado a fingerbot ```/msg fingerbot usuario```


ahora agregamos un bot irc realativamente fácil, yo me instalé uno con docker para probar porque no se como es la comunidad irc [ngircd](https://hub.docker.com/r/linuxserver/ngircd), y de cliente tengo [kvirc](https://www.kvirc.net/) pero la version de portableapps, pero igual son buenas

cabe notar que ese archivo lo tengo en el archivo /etc/users (texto plano) con un formato "usuario:mensaje" separadao por saltos de línea
