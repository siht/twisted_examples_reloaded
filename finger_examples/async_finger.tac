from twisted.application import (
    service,
    strports,
)

from twisted.internet import (
    defer,
    protocol,
    reactor,
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
    protocol = FingerProtocol

    def __init__(self, users):
        self.users = users

    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"No such user"))


def main(): # que no los tac tienen Multiservice?
    global application
    application = service.Application("finger", uid=1, gid=1)
    factory = FingerFactory({b"moshez": b"Happy and well"})
    strports.service("tcp:79", factory, reactor=reactor).setServiceParent(
        service.IServiceCollection(application) # aquí está el multiservice, pero como es una sola aplicación 
    )# pues la dejaron sin la referencia para que otros la puedan tomar


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
