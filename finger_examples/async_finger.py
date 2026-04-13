import email.policy # no tengo idea de porque el xmlrpc falla sin esto, cuando lo corro como un tac

from twisted.application import service
from twisted.internet import (
    defer,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.python import components
from twisted.spread import pb
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


def catchError(err):
    return "Internal error in server"


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        d = self.factory.getUser(user) # obtenermos un deferred al cual podemos colgarle callbacks
        d.addErrback(catchError) # agregamos el error calback

        def writeResponse(message): # esto es una función callback, no tiene self, incluso podría estar fuera de este scope
            self.transport.write(message + b"\r\n")
            self.transport.loseConnection()

        d.addCallback(writeResponse) # agregamos el callback de caso exitoso


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
        user = user.split("!")[0]
        if self.nickname.lower() == channel.lower():
            d = self.factory.getUser(msg.encode("ascii"))
            d.addErrback(catchError)
            d.addCallback(lambda m: f"Status of {msg}: {m}")
            d.addCallback(lambda m: self.msg(user, m))


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

    def _cb_render_GET(self, users, request):
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

    def render_GET(self, request):
        d = self.service.getUsers()
        d.addCallback(self._cb_render_GET, request)

        # signal that the rendering is not complete
        return server.NOT_DONE_YET

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

    def _cb_render_GET(self, status, request):
        request.write(
            b"""<html><head><title>%s</title></head>
        <body><h1>%s</h1>
        <p>%s</p>
        </body></html>"""
            % (self.user, self.user, status)
        )
        request.finish()

    def render_GET(self, request):
        d = self.service.getUser(self.user)
        d.addCallback(self._cb_render_GET, request)
        # signal that the rendering is not complete
        return server.NOT_DONE_YET


class UserStatusXR(xmlrpc.XMLRPC):
    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    def xmlrpc_getUser(self, user):
        print(user)
        return self.service.getUser(user)


class IPerspectiveFinger(Interface):
    def remote_getUser(username):
        """
        Return a user's status.
        """

    def remote_getUsers():
        """
        Return a user's status.
        """


@implementer(IPerspectiveFinger)
class PerspectiveFingerFromService(pb.Root):
    def __init__(self, service):
        self.service = service

    def remote_getUser(self, username):
        return self.service.getUser(username)

    def remote_getUsers(self):
        return self.service.getUsers()


components.registerAdapter(PerspectiveFingerFromService, IFingerService, IPerspectiveFinger)


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
