import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Import your app-level routing files
from bootcamp.notifications.routing import websocket_urlpatterns as notifications_urlpatterns
from bootcamp.messager.routing import websocket_urlpatterns as messager_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local') # Use local settings
#os.environ['ASGI_THREADS'] = "4" # This is not necessary

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                notifications_urlpatterns + messager_urlpatterns # Combine URL patterns
            )
        )
    ),
})