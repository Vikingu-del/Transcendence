from django.urls import path
from .views import start_game, pong_game, save_match_result, match_history, start_new_game, user_match_history


urlpatterns = [
    path("start/", start_game, name="start_game"),
    path("<uuid:game_id>/", pong_game, name="pong_game"),
    path("<uuid:game_id>/save/", save_match_result, name="save_match_result"),
    path("history/", match_history, name="match_history"),
    path('start-new-game/<uuid:game_id>/', start_new_game, name='start_new_game'),
    path('api/match-history/', user_match_history, name='match_history_api'),
    path('api/match-history/<int:user_id>/', user_match_history, name='user_match_history_api'),
    path('match-history/<int:user_id>/', user_match_history, name='user_match_history_direct'),
]
