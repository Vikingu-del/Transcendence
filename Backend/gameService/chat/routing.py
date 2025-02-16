# chat/routing.py

from django.urls import path, re_path
from .consumers import PersonalChatConsumer, OnlineUserConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:id>/", PersonalChatConsumer.as_asgi()),
    path("ws/online_users/", OnlineUserConsumer.as_asgi()),
]
