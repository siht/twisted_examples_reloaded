import sys
import json
import psutil
from twisted.python import log
from twisted.internet import reactor, task
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory


class SystemMonitorProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        self.factory.register_client(self)
        print(f"Cliente conectado: {request.peer}")

    def connectionLost(self, reason):
        self.factory.unregister_client(self)
        print("Cliente desconectado")


class SystemMonitorFactory(WebSocketServerFactory):
    protocol = SystemMonitorProtocol

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = set()
        self.loop = task.LoopingCall(self.broadcast_system_stats)
        self.started_loop = False

    def send_stats(self):
        '''try start loop if not running'''
        theres_clients_conected = self.clients
        are_not_sending_stats = not self.started_loop
        if theres_clients_conected and are_not_sending_stats:
            self.loop.start(1.0, now=False)
            self.started_loop = True

    def stop_sending_stats(self):
        '''try stop loop if running'''
        clients_are_gone = not self.clients
        are_sending_stats = self.started_loop
        if clients_are_gone and are_sending_stats:
            self.loop.stop()
            self.started_loop = False

    def register_client(self, proto):
        self.clients.add(proto)
        self.send_stats()

    def unregister_client(self, proto):
        self.clients.discard(proto)
        self.stop_sending_stats()

    def broadcast_system_stats(self):
        stats = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
        payload = json.dumps(stats).encode('utf8')
        for client in list(self.clients):
            client.sendMessage(payload, False)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = SystemMonitorFactory()
    reactor.listenTCP(9000, factory)
    reactor.run()
