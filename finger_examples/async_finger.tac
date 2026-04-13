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


class FingerSetterProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def connectionLost(self, reason):
        user = self.lines[0]
        status = self.lines[1]
        self.factory.setUser(user, status)


class FingerSetterFactory(protocol.ServerFactory):
    protocol = FingerSetterProtocol

    def __init__(self, fingerFactory):
        self.fingerFactory = fingerFactory

    def setUser(self, user, status):
        self.fingerFactory.users[user] = status


def main(): # que no los tac tienen Multiservice?
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    ff = FingerFactory({b"moshez": b"Happy and well"})
    fsf = FingerSetterFactory(ff)

    strports.service("tcp:79", ff, reactor=reactor).setServiceParent(serviceCollection)
    strports.service("tcp:1079", fsf).setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
