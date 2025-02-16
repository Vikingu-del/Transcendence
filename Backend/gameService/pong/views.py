from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import GameSession
import uuid
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q

@login_required
def start_game(request):
    if not request.user.is_authenticated:
        return redirect('login')

    existing_game = GameSession.objects.filter(player1=request.user, player2=None).first()
    if existing_game:
        return JsonResponse({"invite_link": existing_game.get_invite_link()})

    game = GameSession.objects.create(player1=request.user)
    return JsonResponse({"invite_link": game.get_invite_link()})

@login_required
def pong_game(request, game_id):
    game = get_object_or_404(GameSession, id=game_id)

    if not request.user.is_authenticated:
        return redirect('login')

    # Assign player2 if needed
    if game.player1 != request.user and game.player2 is None:
        game.player2 = request.user
        game.save()

    # Ensure only the two players can access the game
    if game.player1 != request.user and game.player2 != request.user:
        return HttpResponse("This game is full.", status=403)

    return render(request, "pong/game.html", {
        "game": game,
        "player1": game.player1.username,
        "player2": game.player2.username if game.player2 else "Waiting for player 2..."
    })

@csrf_exempt
@login_required
def save_match_result(request, game_id):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            game = GameSession.objects.get(id=game_id)
            game.player1_score = data["player1_score"]
            game.player2_score = data["player2_score"]
            game.winner = game.player1 if data["player1_score"] > data["player2_score"] else game.player2
            game.ended_at = now()  # Mark the game as ended
            game.is_active = False  # Mark as inactive
            game.save()

            return JsonResponse({"status": "Game ended and recorded!"})
        except GameSession.DoesNotExist:
            return JsonResponse({"error": "Game not found"}, status=404)

@login_required
def match_history(request):
    """Display all past matches for the logged-in user."""
    matches = GameSession.objects.filter(player1=request.user) | GameSession.objects.filter(player2=request.user)
    matches = matches.filter(is_active=False).order_by("-ended_at")

    return render(request, "pong/match_history.html", {"matches": matches})

@login_required
def start_new_game(request, game_id):
    if request.method == "POST":
        old_game = get_object_or_404(GameSession, id=game_id)
        new_game = GameSession.objects.create(player1=old_game.player1, player2=old_game.player2)
        new_game.is_active = True
        new_game.save()

        return JsonResponse({"new_game_url": f"/pong/{new_game.id}/"})  

    return JsonResponse({"error": "Invalid request"}, status=400)

