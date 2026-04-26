import os
from flask import Flask
from werkzeug.wrappers import Request, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from django.core.wsgi import get_wsgi_application


@Request.application
def werkzeug_admin_backdoor(request):
    return Response(
        "<h1>Consola Werkzeug</h1><p>Estás fuera del alcance de Django.</p>",
        mimetype='text/html'
    )


flask_app = Flask(__name__)

@flask_app.route("/")
def hello():
    return "¡Hola! Soy Flask viviendo en el mismo proceso que Django."


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

django_app = get_wsgi_application()


application = DispatcherMiddleware(django_app, {
    '/travieso2': werkzeug_admin_backdoor,
    '/flask': flask_app
})
