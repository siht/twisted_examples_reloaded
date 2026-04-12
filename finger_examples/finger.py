from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.web import client


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
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol

    def __init__(self, prefix):
        self.prefix = prefix

    def getUser(self, user):
        return client.getPage(self.prefix + user) # oh no. twisted ya no tiene esto :c


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory(prefix=b"http://livejournal.com/~")) # y encima esta url ya no existe
    reactor.run()


if __name__ == '__main__':
    main()
