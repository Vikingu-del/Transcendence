from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Main notification WebSocket (handles friend requests, status updates)
    re_path(
        r'ws/profile/notifications/$', 
        consumers.NotificationConsumer.as_asgi()
    ),
]