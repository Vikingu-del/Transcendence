from django.urls import re_path
from . import consumers
from tournament.consumers import TournamentConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<game_id>[\w-]+)/$', consumers.PongConsumer.as_asgi()),
	re_path(r'ws/tournament/(?P<tournament_id>[\w-]+)/$', TournamentConsumer.as_asgi()),
]