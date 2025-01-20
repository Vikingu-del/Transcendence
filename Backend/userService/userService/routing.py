from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/profile/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),  # Updated this line
]