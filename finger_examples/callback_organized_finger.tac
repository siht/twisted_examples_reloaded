import sys
sys.path += '.'

import callback_finger

from twisted.application import (
    internet,
    service,
    strports,
)
from twisted.internet import (
    endpoints,
    reactor,
)
from twisted.spread import pb
from twisted.web import (
    resource,
    server,
)


def main(): # quitamos la construcción de los factories aquí y los centralizamos en un service
    global application
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = service.IServiceCollection(application) # ves es el multiservice

    f = callback_finger.FingerService("/etc/users")
    finger = strports.service("tcp:79", callback_finger.IFingerFactory(f)) # no te confundas esto es un servicio como el de arriba
    # solo que está envolviendo a nuestro factory, es un StreamServerEndpointService
    site = server.Site(resource.IResource(f))
    webfinger = strports.service("tcp:8000", site) # no lo se pero supongo que Site
    # es un tipo de servicio que acepta resources para mostrar
    i = callback_finger.IIRCClientFactory(f)
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
    strports.service(
        "tcp:8889", pb.PBServerFactory(callback_finger.IPerspectiveFinger(f))
    ).setServiceParent(serviceCollection)
    strports.service(
        "ssl:port=443:certKey=cert.pem:privateKey=key.pem", site
    ).setServiceParent(serviceCollection)


if __name__ == 'builtins': # cuando twistd llama a un tac el archivo se llama "builtins"
    main()
