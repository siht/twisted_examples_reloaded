from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.web import client


def getPage(url):
    agent = client.Agent(reactor)
    d = agent.request(
        b'GET',
        url,
        client.Headers({'User-Agent': [b'Twisted Finger Server']}),
        None
    )
    
    def cbResponse(response):
        return client.readBody(response)
    
    d.addCallback(cbResponse)
    return d


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

    def __init__(self, sufix):
        self.sufix = sufix

    def getUser(self, user):
        return getPage(b'https://'+user+self.sufix)


def main(): # no es necesaria esta función, pero se ve más agrupado
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory(sufix=b".livejournal.com/")) # nueva url, aunque es https ahora
    reactor.run()


if __name__ == '__main__':
    main()
