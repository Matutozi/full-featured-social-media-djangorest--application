import os
import django
django.setup()
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

#from channels.security.websocket import AllowedHostsOriginValidator
from message_app.routing import websocket_urlpatterns as message_app_websocket
from posts.routing import websocket_urlpatterns as posts_websocket


application = get_asgi_application()

websocket_urlpatterns = message_app_websocket + posts_websocket

application = ProtocolTypeRouter(
    {
        "http": application,
        "websocket": (
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)
