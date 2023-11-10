from django.urls import path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bootcamp.messager.consumers import MessagerConsumer
from bootcamp.notifications.consumers import NotificationsConsumer

# from bootcamp.notifications.routing import notifications_urlpatterns
# from bootcamp.messager.routing import messager_urlpatterns

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path(r"^notifications/$", NotificationsConsumer),
                        path(r"^(?P<username>[^/]+)/$", MessagerConsumer),
                    ]
                )
            )
        )
    }
)
