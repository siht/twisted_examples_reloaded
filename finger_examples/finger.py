from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)
from twisted.protocols import basic


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user): # ahora espera un parámetro
        self.transport.loseConnection() # y se sigue desconectando


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
