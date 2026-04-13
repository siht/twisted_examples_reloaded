import html

from twisted.application import (
    service,
    strports,
)
from twisted.internet import (
    defer,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.web import (
    resource,
    server,
    static,
)


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


class FingerResource(resource.Resource):
    def __init__(self, users):
        self.users = users
        resource.Resource.__init__(self) # es un super, pero meh

    # we treat the path as the username
    def getChild(self, username, request):
        """
        'username' is L{bytes}.
        'request' is a 'twisted.web.server.Request'.
        """
        messagevalue = self.users.get(username)
        if messagevalue:
            messagevalue = messagevalue.decode("ascii")
        if type(username) == bytes:
            username = username.decode("ascii")
        username = html.escape(username)
        if messagevalue is not None:
            messagevalue = html.escape(messagevalue)
            text = f"<h1>{username}</h1><p>{messagevalue}</p>"
        else:
            text = f"<h1>{username}</h1><p>No such user</p>"
        text = text.encode("ascii")
        return static.Data(text, "text/html")


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
        r = FingerResource(self.users)
        return r


def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    f = FingerService("/etc/users")
    finger = strports.service("tcp:79", f.getFingerFactory()) # no te confundas esto es un servicio como el de arriba
    # solo que está envolviendo a nuestro factory, es un StreamServerEndpointService
    webfinger = strports.service("tcp:8000", server.Site(f.getResource())) # no lo se pero supongo que Site
    # es un tipo de servicio que acepta resources para mostrar

    finger.setServiceParent(serviceCollection)
    f.setServiceParent(serviceCollection)
    webfinger.setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
