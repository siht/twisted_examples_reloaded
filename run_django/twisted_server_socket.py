from twisted.internet import reactor, protocol

class ProxyToUnix(protocol.Protocol):
    """
    Este es el lado que habla con el usuario (TCP).
    """
    def connectionMade(self):
        print("Recibida conexión TCP. Abriendo puente al Unix Socket...")
        factory = protocol.ClientFactory()
        factory.protocol = UnixBridge
        factory.server_side = self
        reactor.connectUNIX("/tmp/my_app.sock", factory)

    def dataReceived(self, data):
        if hasattr(self, 'unix_side'):
            self.unix_side.transport.write(data)

    def connectionLost(self, reason):
        if hasattr(self, 'unix_side'):
            self.unix_side.transport.loseConnection()

class UnixBridge(protocol.Protocol):
    """
    Este es el lado que habla con el archivo .sock (Unix).
    """
    def connectionMade(self):
        # Enlazamos ambos protocolos
        self.factory.server_side.unix_side = self
        print("Puente establecido.")

    def dataReceived(self, data):
        # Lo que responde el socket, se manda de vuelta al usuario TCP
        self.factory.server_side.transport.write(data)

    def connectionLost(self, reason):
        self.factory.server_side.transport.loseConnection()

# Lanzamiento
if __name__ == "__main__":
    factory = protocol.ServerFactory()
    factory.protocol = ProxyToUnix
    
    print("Proxy activo: Escuchando en TCP 8080 -> Redirigiendo a /tmp/my_app.sock")
    reactor.listenTCP(8080, factory)
    reactor.run()
