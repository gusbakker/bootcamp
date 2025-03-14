from django.urls import re_path  # Use re_path for compatibility
from . import consumers

websocket_urlpatterns = [
    re_path(r"^(?P<username>[^/]+)/$", consumers.MessagerConsumer.as_asgi()),
]