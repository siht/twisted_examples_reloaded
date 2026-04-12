from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)


class FingerProtocol(protocol.Protocol):
    # tiene métodos que manejasn la llegada y envio de datos pero no hacen nada
    pass


class FingerFactory(protocol.ServerFactory):
    # inicia el protocolo y maneja persitencia
    protocol = FingerProtocol


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
