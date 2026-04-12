from twisted.internet import (
    endpoints,
    protocol,
    reactor,
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


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
