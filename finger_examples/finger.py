from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)


class FingerProtocol(protocol.Protocol):
    def connectionMade(self): # reescribimos el método para que haga algo
        self.transport.loseConnection() # como... desconectarse...


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persistencia
    protocol = FingerProtocol


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
