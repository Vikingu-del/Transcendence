from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from pong.models import GameSession

@login_required
def pong_game(request, game_id):
    game = get_object_or_404(GameSession, id=game_id)

    if not game.player2 and game.player1 != request.user:
        game.player2 = request.user
        game.save()

    return render(request, "pong_ws/pong_game.html", {"game": game})

@login_required    
def game_view(request, game_id):
    return render(request, 'pong_ws/pong_game.html')