from twisted.application import (
    internet,
    service,
    strports,
)
from twisted.internet import (
    defer,
    endpoints,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.web import (
    resource,
    server,
    static,
)
from twisted.words.protocols import irc


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


class IRCReplyBot(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)

    def privmsg(self, user, channel, msg):
        user = user.split("!")[0]
        if self.nickname.lower() == channel.lower():
            d = self.factory.getUser(msg.encode("ascii"))

            def onError(err):
                return b"Internal error in server"

            d.addErrback(onError)

            def writeResponse(message):
                message = message.decode("ascii")
                irc.IRCClient.msg(self, user, msg + ": " + message)

            d.addCallback(writeResponse)


class FingerService(service.Service):
    def __init__(self, filename):
        self.users = {}
        self.filename = filename

    def _read(self):
        with open(self.filename, "rb") as f:
            for line in f:
                user, status = line.split(b":", 1)
                user = user.strip()
                status = status.strip()
                self.users[user] = status
        self.call = reactor.callLater(30, self._read)

    def startService(self):
        self._read()
        service.Service.startService(self) # esto es el super() pero la forma antigua

    def stopService(self):
        service.Service.stopService(self)  # esto es el super() pero la forma antigua
        self.call.cancel()

    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"No such user"))

    def getFingerFactory(self):
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f

    def getResource(self):
        def getData(path, request):
            user = self.users.get(path, b"No such users <p/> usage: site/user")
            path = path.decode("ascii")
            user = user.decode("ascii")
            text = f"<h1>{path}</h1><p>{user}</p>"
            text = text.encode("ascii")
            return static.Data(text, "text/html")

        r = resource.Resource()
        r.getChild = getData
        return r

    def getIRCBot(self, nickname):
        f = protocol.ClientFactory()
        f.protocol = IRCReplyBot
        f.nickname = nickname
        f.getUser = self.getUser
        return f


def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    f = FingerService("/etc/users")
    finger = strports.service("tcp:79", f.getFingerFactory()) # no te confundas esto es un servicio como el de arriba
    # solo que está envolviendo a nuestro factory, es un StreamServerEndpointService
    webfinger = strports.service("tcp:8000", server.Site(f.getResource())) # no lo se pero supongo que Site
    # es un tipo de servicio que acepta resources para mostrar
    ircfinger = internet.ClientService( # antiguo freenode o liberachat
        #endpoints.clientFromString(reactor, "tcp:irc.freenode.org:6667"), 
        #endpoints.clientFromString(reactor, "tcp:irc.liberachat.chat:6667"), 
        endpoints.clientFromString(reactor, "tcp:127.0.0.1:6667"), # yo mejor me instalo mi propio server de irc para no molestar
        f.getIRCBot("fingerbot"), # asegurate de que el nombre de tu bot no sea muy largo a veces da error y no te notifica
    )

    finger.setServiceParent(serviceCollection)
    f.setServiceParent(serviceCollection)
    webfinger.setServiceParent(serviceCollection)
    ircfinger.setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
