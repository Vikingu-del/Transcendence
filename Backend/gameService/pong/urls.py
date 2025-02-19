from django.urls import path
from .views import start_game, pong_game, save_match_result, match_history, start_new_game

urlpatterns = [
    path("start/", start_game, name="start_game"),
    path("<uuid:game_id>/", pong_game, name="pong_game"),
    path("<uuid:game_id>/save/", save_match_result, name="save_match_result"),
    path("history/", match_history, name="match_history"),
    path('start-new-game/<uuid:game_id>/', start_new_game, name='start_new_game'),
]
