import os
from werkzeug.wrappers import Request, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.internet.address import UNIXAddress

from settings.wsgi import application as django_and_werkzeug_app

# 1. Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django_app = django_and_werkzeug_app

@Request.application
def werkzeug_view(request):
    return Response(
        "<h1>¡Soy Werkzeug viviendo dentro de Django!</h1>"
        "<p>Django ni siquiera sabe que existo.</p>",
        mimetype='text/html'
    )


combined_app = DispatcherMiddleware(django_app, {
    '/travieso': werkzeug_view
})

# 2. La Solución: Clase para manejar Sockets Unix sin errores
class UnixWSGIResource(WSGIResource):
    def render(self, request):
        # 1. Corregimos la dirección del Cliente (Remote)
        client_addr = request.getClientAddress()
        if isinstance(client_addr, UNIXAddress):
            if not hasattr(client_addr, 'host'):
                client_addr.host = b'127.0.0.1'
            if not hasattr(client_addr, 'port'):
                client_addr.port = 0

        # 2. Corregimos la dirección del Servidor (Host/Local)
        # Esto es lo que causó el último Traceback
        server_addr = request.getHost()
        if isinstance(server_addr, UNIXAddress):
            if not hasattr(server_addr, 'host'):
                # SERVER_NAME usualmente espera el nombre del host
                server_addr.host = b'localhost'
            if not hasattr(server_addr, 'port'):
                # SERVER_PORT para WSGI
                server_addr.port = 80 
        
        return super().render(request)

# 3. Instanciamos nuestra clase corregida
resource = UnixWSGIResource(reactor, reactor.getThreadPool(), combined_app)
site = Site(resource)

socket_path = "/tmp/my_app.sock"

# Limpieza preventiva: si el archivo existe de una ejecución previa, lo borramos
if os.path.exists(socket_path):
    os.remove(socket_path)

# 4. Lanzamiento
reactor.listenUNIX(socket_path, site)

print(f"Twisted + Django funcionando en: {socket_path}")
reactor.run()