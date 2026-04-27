import sys
from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory


class ChatProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        self.factory.register_client(self)

    def connectionLost(self, reason):
        self.factory.unregister_client(self)

    def onMessage(self, payload, isBinary):
        for client in self.factory.clients:
            client.sendMessage(payload, isBinary)


class ChatFactory(WebSocketServerFactory):
    protocol = ChatProtocol

    def __init__(self):
        super().__init__()
        self.clients = set()

    def register_client(self, proto):
        self.clients.add(proto)

    def unregister_client(self, proto):
        self.clients.discard(proto)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = ChatFactory()
    reactor.listenTCP(9000, factory)
    reactor.run()