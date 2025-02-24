import os
import django

# Set Django settings module and initialize Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gameService.settings')
django.setup()

# Import after Django initialization
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from pong_ws import routing
from django.contrib.auth import get_user_model
from .middleware import TokenAuthMiddleware  # Import middleware after Django setup

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

# Create the application instance
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(routing.websocket_urlpatterns)
        )
    ),
})