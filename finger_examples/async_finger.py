from twisted.internet import (
    defer,
    endpoints,
    protocol,
    task,
)
from twisted.protocols import basic


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user): # twisted inició con las marcas sincronas de python
        defer.ensureDeferred(self.handle_line(user)) # sólo tenemos que "marcar" que estamos recibiendo un deferred

    async def handle_line(self, user): # marcamos async para usar await dentro del método
        try:
            # Get the result from the factory
            result = await self.factory.getUser(user)
            self.transport.write(result + b"\r\n")
        except Exception:
            self.transport.write(b"Internal error in server\r\n")
        finally:
            self.transport.loseConnection()


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol

    def __init__(self, users):
        self.users = users

    def getUser(self, user): # regresa un deferred, no lo marcamos async
        return defer.succeed(self.users.get(user, b"No such user")) # convertimos lo sincrono en asincrono


async def main(reactor):
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory({b"moshez": b"Happy and well"}))
    # la siguiente instrucción no es una forma de arrancar el reactor
    # simplemente regresa un deferred para que no se acabe el bucle
    await defer.Deferred() 
    


# no es necesario esta línea tan larga sólo es para que veas donde se ponen los argumentos
# por línea de comando, pero la dejo para futuras referencias
# task.react(lambda *a: defer.ensureDeferred(main(*a)), sys.argv[1:])

task.react(lambda reactor: defer.ensureDeferred(main(reactor))) # este es el que provee y arranca el reactor
