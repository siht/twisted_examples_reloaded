from twisted.internet import (
    defer,
    endpoints,
    protocol,
    task,
)
from twisted.protocols import basic


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user): # ahora espera un parámetro
        # ahora regresamos "algo" pero desde el factory
        # si leiste el README.md los protocolos no deben tener datos
        self.transport.write(self.factory.getUser(user) + b"\r\n")
        self.transport.loseConnection() # y se sigue desconectando


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol

    def getUser(self, user): # "persistencia" de momento
        return b"No such user" # regresamos un "error"


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
