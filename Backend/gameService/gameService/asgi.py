# import os

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_proj.settings")

# django_asgi_app = get_asgi_application()

# from chat.routing import websocket_urlpatterns

# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(
#             AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
#         ),
#     }
# )

# test_proj/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_proj.settings')

import chat.routing
import pong_ws.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns)),
    "websocket": AuthMiddlewareStack(URLRouter(pong_ws.routing.websocket_urlpatterns)),
})
