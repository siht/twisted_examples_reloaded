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


class FingerSetterProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def connectionLost(self, reason):
        user = self.lines[0]
        status = self.lines[1]
        self.factory.setUser(user, status)


class FingerService(service.Service):
    def __init__(self, users):
        self.users = users

    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"No such user"))

    def setUser(self, user, status):
        self.users[user] = status

    def getFingerFactory(self): # centralizamos la construccion de los factories
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f

    def getFingerSetterFactory(self): # centralizamos la construccion de los factories
        f = protocol.ServerFactory()
        f.protocol = FingerSetterProtocol
        f.setUser = self.setUser
        return f


def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    f = FingerService({b"moshez": b"Happy and well"})

    # centralizado el factory ahora tenemos más limpieza
    strports.service("tcp:79", f.getFingerFactory(), reactor=reactor).setServiceParent(serviceCollection)
    strports.service("tcp:1079", f.getFingerSetterFactory()).setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
