from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Main notification WebSocket (handles friend requests, status updates)
    re_path(
        r'^ws/api/user/notifications/$',
        consumers.NotificationConsumer.as_asgi()
    ),
    
    # Chat WebSocket with chat_id parameter
    re_path(
        r'^ws/api/user/chat/(?P<chat_id>[^/]+)/$',
        consumers.ChatConsumer.as_asgi()
    ),
]