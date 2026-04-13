import email.policy # no tengo idea de porque el xmlrpc falla sin esto, cuando lo corro como un tac

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
from twisted.python import components
from twisted.web import (
    resource,
    server,
    xmlrpc,
)
from twisted.words.protocols import irc

from zope.interface import Interface, implementer


class IFingerService(Interface):
    def getUser(user):
        """
        Return a deferred returning L{bytes}.
        """

    def getUsers():
        """
        Return a deferred returning a L{list} of L{bytes}.
        """


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user): # twisted inició con las marcas sincronas de python
        defer.ensureDeferred(self.handle_line(user)) # sólo tenemos que "marcar" que estamos recibiendo un deferred

    async def handle_line(self, user): # marcamos async para usar await dentro del método
        try:
            # Get the result from the factory
            result = await self.factory.getUser(user)
            self.transport.write(result + b"\r\n")
        except Exception:
            self.transport.write(b"Internal error in server\r\n")
        finally:
            self.transport.loseConnection()


class IFingerFactory(Interface):
    def getUser(user):
        """
        Return a deferred returning L{bytes}
        """

    def buildProtocol(addr):
        """
        Return a protocol returning L{bytes}
        """


@implementer(IFingerFactory)
class FingerFactoryFromService(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, service):
        self.service = service

    def getUser(self, user):
        return self.service.getUser(user)


components.registerAdapter(FingerFactoryFromService, IFingerService, IFingerFactory)


class IRCReplyBot(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)

    def privmsg(self, user, channel, msg):
        defer.ensureDeferred(self.handle_privmsg(user, channel, msg))

    async def handle_privmsg(self, user, channel, msg):
        user = user.split("!")[0]
        if self.nickname.lower() == channel.lower():
            inner_user = await self.factory.getUser(msg.encode("ascii"))
            try:
                message = inner_user.decode("ascii")
                self.msg(user, f"Status of {msg}: {message}")
            except Exception as err:
                self.msg(b"Internal error in server")


class IIRCClientFactory(Interface):
    """
    @ivar nickname
    """

    def getUser(user):
        """
        Return a deferred returning a string.
        """

    def buildProtocol(addr):
        """
        Return a protocol.
        """


@implementer(IIRCClientFactory)
class IRCClientFactoryFromService(protocol.ClientFactory):
    protocol = IRCReplyBot
    nickname = None

    def __init__(self, service):
        self.service = service

    def getUser(self, user):
        return self.service.getUser(user)


components.registerAdapter(
    IRCClientFactoryFromService, IFingerService, IIRCClientFactory
)


@implementer(resource.IResource)
class UserStatusTree(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.putChild(b"RPC2", UserStatusXR(self.service))

    def render_GET(self, request):
        defer.ensureDeferred(self.handle_render_GET(request))
        return server.NOT_DONE_YET

    async def handle_render_GET(self, request):
        users = await self.service.getUsers()
        userOutput = "".join(
            [f'<li><a href="{user.decode('ascii')}">{user.decode('ascii')}</a></li>' for user in users]
        )
        request.write(
            ("""
            <html><head><title>Users</title></head><body>
            <h1>Users</h1>
            <ul>
            %s
            </ul></body></html>"""
            % userOutput).encode('ascii')
        )
        request.finish()

    def getChild(self, path, request):
        if path == b"":
            return UserStatusTree(self.service)
        else:
            return UserStatus(path, self.service)


components.registerAdapter(UserStatusTree, IFingerService, resource.IResource)


class UserStatus(resource.Resource):
    def __init__(self, user, service):
        resource.Resource.__init__(self)
        self.user = user
        self.service = service

    def render_GET(self, request):
        defer.ensureDeferred(self.handle_render_GET(request))
        return server.NOT_DONE_YET

    async def handle_render_GET(self, request):
        status = await self.service.getUser(self.user)
        request.write(
            b"""<html><head><title>%s</title></head>
            <body><h1>%s</h1>
            <p>%s</p>
            </body></html>"""
                % (self.user, self.user, status)
        )
        request.finish()


class UserStatusXR(xmlrpc.XMLRPC):
    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    def xmlrpc_getUser(self, user):
        return self.service.getUser(user)


@implementer(IFingerService)
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
        if isinstance(user, str):
            user = user.encode("ascii")
        return defer.succeed(self.users.get(user, b"No such user"))

    def getUsers(self):
        return defer.succeed(list(self.users.keys()))


def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    f = FingerService("/etc/users")
    finger = strports.service("tcp:79", IFingerFactory(f)) # no te confundas esto es un servicio como el de arriba
    # solo que está envolviendo a nuestro factory, es un StreamServerEndpointService
    webfinger = strports.service("tcp:8000", server.Site(resource.IResource(f))) # no lo se pero supongo que Site
    # es un tipo de servicio que acepta resources para mostrar
    i = IIRCClientFactory(f)
    i.nickname = "fingerbot" # asegurate de que el nombre de tu bot no sea muy largo a veces da error y no te notifica
    ircfinger = internet.ClientService( # antiguo freenode o liberachat
        #endpoints.clientFromString(reactor, "tcp:irc.freenode.org:6667"), 
        #endpoints.clientFromString(reactor, "tcp:irc.liberachat.chat:6667"), 
        endpoints.clientFromString(reactor, "tcp:127.0.0.1:6667"), # yo mejor me instalo mi propio server de irc para no molestar
        i
    )

    finger.setServiceParent(serviceCollection)
    f.setServiceParent(serviceCollection)
    webfinger.setServiceParent(serviceCollection)
    ircfinger.setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
