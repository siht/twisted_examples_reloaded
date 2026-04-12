# twisted_examples_reloaded
examples from twisted

## licencia de la siguiente explicación

El texto explicativo (no el código) está bajo licencia CC-BY-4.0

## como explicar twisted "fácil" (twisted cheat sheet)
twisted es una librería asíncrona que permite la comunicación en red, o sea no se limita a hacer servidores, también clientes. Además incluye una parte de componentización con acoplamiento débil

## términología que te puede ayudar a comprender
Pese a que twisted tiene su documentación, no he sido capaz de encontrar una guía directa que me haya podido ayudar a aprender twisted, así que sugiero que si ves mis ejemplos en código y no entiendas algo y quieras leer la documentación de twisted te recomiendo que vayas con este markdown para entender más rápido. Por cierto esto no es una manera sencilla de ver twisted, si necesitas profundizar con la documentación y con un recurso de krondo, que explica mucho de lo que yo dejé grosso modo, pero si te gana el tiempo ve lo que puse y trata de entender con eso el código.

### twisted
Antes de entrar ¿cómo se ve todo esto en código?

Factory(Protocol(transport)) -- una aplicación muy simple

Application(Multiservice(Service(Factory(Protocol(transport))))) -- una aplicación que funciona como servicio

El reactor no encierra a nadie porque todos los elementos que usa twisted están encadenados a él.

* transport. Es una objeto que permite la comunicación bidireccional (recibes y mandas datos), lo que escribas aquí es el destinatario o lo que algunos les gusta llamar "la tubería", además de que recibes datos por este mismo medio. En protocols avanzados, sólo accedes a el mediante métodos (como sendLine).
* protocol. Tal cual es un protocolo (ejemplos: http, smtp, websocket) de cualquier tipo en red, este encapsula a transport, ojo este se destruye al terminar la comunicación por lo tanto no guarda estados, siempre hay una referencia hacía su factory que si se mantiene vivo.
* factory. Este se encarga de construir un protocolo y a su vez este se mantiene activo durante toda la ejecución, aquí es donde se ponen variables, persistencia, estados, etc, no es necesariamente el lugar donde se pone la lógica de negocio, pero si tu quieres, pues nada te detiene, aunque yo te recomiendo inyectarla. Este no es necesario en una comunicación UDP.
* service. Míralo como un daemon, pero a nivel de twisted, en vez de que el SO se encarge de gestionarlo, lo gestionas tú con twisted.
* multiservice. Sirve para poder arrancar multiples servicios con twisted podríamos decir que sería el gestor de alto nivel de daemons en twisted.
* application. Es el punto donde se engancha ahora si con el sistema operativo, esto es especifico de archivos ".tac" (es imperativo que esa variable sea global ya se por scope o porque la definiste con global y se llame "application").
* asíncronicidad. no ejecuta paralelamente (no son hilos), espera lo que llega de red y llama al componente cuando es necesario, de esto se encarga el reactor.
* reactor. Es un patrón de diseño, pero explicado "rápido": es un bucle que no está preguntando cuando llegó un dato, está a la espera pasiva de mensajes y sólo así empieza a hacer alguna acción que esté pendiente, así funciona "TODOS" los "lenguajes asíncronos", muy similar a un observer (mezclado con una especie de round robin, digo no es la mejor manera de explicarlo, pero es para ganar tiempo, si quieres estudiarlo por ti mismo es mucho más allá de esta simple explicación).
* deferred. es la forma en que twisted maneja una acción que no está hecha y a esta se le cuelgan los callbacks de éxito y error, también conocidas como "promesas". Las promesas son manejadas por el reactor quien está a la espera de que estas promesas sean completadas. Para twisted no es necesario manejar deferreds puede hacer acciones bloqueantes como buscar en un diccionario, pero por ejemplo si pones una operación que tarde mucho y no se ejecuta en el reactor de manera asíncrona esta puede bloquear el reactor y pues no tendría mucho sentido tener uno, por ejemplo poner un time.sleep, recuerda poner la versión asíncrona o en todo caso volverla una task.

en la página hay ejemplos agregando que es posible hacerlo con la sintaxis async await de python, hay que notar que task.react, no cambia nada de lo que he puesto sólo que task react ahora inyecta el reactor y lo inicia por tí.

Veamos este ejemplo:

```python

import sys, os

from twisted.internet import protocol, defer, endpoints, task
from twisted.conch.endpoints import SSHCommandClientEndpoint

async def main(reactor, username="alice", sshhost="example.com", portno="22"):
    envAgent = endpoints.UNIXClientEndpoint(reactor, os.environ["SSH_AUTH_SOCK"])
    endpoint = SSHCommandClientEndpoint.newConnection(
        reactor, "echo 'hello world'", username, sshhost,
        int(portno), agentEndpoint=envAgent,
    )

    class ShowOutput(protocol.Protocol):
        received = b""
        def dataReceived(self, data):
            self.received += data
        def connectionLost(self, reason):
            finished.callback(self.received)

    finished = defer.Deferred()
    factory = protocol.Factory.forProtocol(ShowOutput)
    await endpoint.connect(factory)
    print("SSH response:", await finished)

task.react(lambda *a, **k: defer.ensureDeferred(main(*a, **k)), sys.argv[1:])

```

Pese a que no he leído la documentación, parece ser que task.react pone los argumentos de "a" de la función anónima, y deja espacio para los key values (k), los cuales son pasados a main, y el parámetro final parece ser sólo las claves valor que pueden ser sobre escritas vía línea de comandos, de ahí en fuera pues todo quisieron encapsularlo en la función main (Protocolo incluido), aunque por lo visto es solamente la parte de configuración, porque todo lo demás parece que puede convivir tal cual expuse.

### zope.interface

No es necesario para que twisted funcione, pero los ejemplos a veces llevan esto y confunden un poco (o un mucho en mi caso), sólo es para que navegues con menos miedo entre el código.

zope.interface es una librería que te permite hacer componentes con reglas duras como interfaces en vez de las reglas blandas como el duck typing.

* component. Es una pieza de software que se puede reemplazar (fácil o difícil depende de como la hayas construido).
* interface. Es un recordatorio al programador de que debe hacer cada método tipo de datos de entrada o salida (contrato), estos idealmente deben seguirse al pie de la letra, sin embargo python no obliga a hacerlo, y zope.interface puede hacer que los cumplas con ciertas instrucciones.
* adapter. Básicamente es un pedazo de código que hace que se cumpla la interfaz, cuando llegan tipos de datos diferente, tu debes hacer un adaptador para que convierta el tipo de datos que te llego a algo que si puede entender tu propio sistema.
* contenedor IoC (no se dice en los textos, y es más es muy probable que no sea el concepto pero huele igual). este es una combinación de twisted y zope.interface. "from twisted.python.components.registerAdapter", no inyectas directamente tu adaptador, lo registras y este en tiempo de ejecución decide que adaptador usar, se puede ver en los códigos como que "instancias" una interface con un objeto: IInterface(objeto), aunque realmente se usa como una función que te regresa el adapter previamente registrado. Esto es algo impensable en Java o C#, donde las interfaces sólo son una especie de tag que indica que ahí va a recibir un objeto que implementó la interfaz.
