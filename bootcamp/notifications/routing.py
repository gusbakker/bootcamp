from django.urls import re_path  # Use re_path for compatibility
from . import consumers

websocket_urlpatterns = [
    re_path(r"^notifications/$", consumers.NotificationsConsumer.as_asgi()),
]