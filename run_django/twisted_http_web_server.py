import os
import sys
from django.core.wsgi import get_wsgi_application
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.python import log

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
    django_app = get_wsgi_application()
    site = Site(WSGIResource(reactor, reactor.getThreadPool(), django_app))
    log.startLogging(sys.stdout)
    reactor.listenTCP(8000, site)
    reactor.run()
