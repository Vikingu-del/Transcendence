from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pong/', include('pong.urls')), # local multiplayer
    path('pong-ws/', include('pong_ws.urls')), # remote multiplayer
    path('', include('chat.urls')),
]
