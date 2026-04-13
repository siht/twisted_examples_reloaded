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
    def lineReceived(self, user):
        d = self.factory.getUser(user) # obtenermos un deferred al cual podemos colgarle callbacks

        def onError(err): # esto es una función callback, no tiene self, incluso podría estar fuera de este scope
            return "Internal error in server"

        d.addErrback(onError) # agregamos el error calback

        def writeResponse(message): # esto es una función callback, no tiene self, incluso podría estar fuera de este scope
            self.transport.write(message + b"\r\n")
            self.transport.loseConnection()

        d.addCallback(writeResponse) # agregamos el callback de caso exitoso


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
