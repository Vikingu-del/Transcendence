from django.urls import path
from .views import pong_game
from . import views

urlpatterns = [
    # path("<uuid:game_id>/", pong_game, name="pong_game"),
    path('<uuid:game_id>/', views.game_view, name='pong_game'),
]
