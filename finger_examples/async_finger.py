from twisted.internet import (
    defer,
    endpoints,
    protocol,
    task,
)


class FingerProtocol(protocol.Protocol):
    def connectionMade(self): # reescribimos el método para que haga algo
        self.transport.loseConnection() # como... desconectarse...


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol


async def main(reactor):
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    # la siguiente instrucción no es una forma de arrancar el reactor
    # simplemente regresa un deferred para que no se acabe el bucle
    await defer.Deferred() 
    


# no es necesario esta línea tan larga sólo es para que veas donde se ponen los argumentos
# por línea de comando, pero la dejo para futuras referencias
# task.react(lambda *a: defer.ensureDeferred(main(*a)), sys.argv[1:])

task.react(lambda reactor: defer.ensureDeferred(main(reactor))) # este es el que provee y arranca el reactor
