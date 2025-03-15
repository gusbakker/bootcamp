from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bootcamp.messager.consumers import MessagerConsumer
from bootcamp.notifications.consumers import NotificationsConsumer

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        # Use re_path for regex patterns, not path
                        re_path(r"notifications/$", NotificationsConsumer.as_asgi()),
                        re_path(r"(?P<username>[^/]+)/$", MessagerConsumer.as_asgi()),
                    ]
                )
            )
        )
    }
)