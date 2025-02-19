from django.db import models

from django.contrib.auth.models import User
import uuid

# models.py

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player1 = models.ForeignKey(User, related_name="games_as_player1", on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name="games_as_player2", null=True, blank=True, on_delete=models.CASCADE)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(User, related_name="games_won", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Game-specific state
    player1_paddle = models.IntegerField(default=0)  # Y position of player 1 paddle
    player2_paddle = models.IntegerField(default=0)  # Y position of player 2 paddle
    ball_position = models.JSONField(default=dict)  # Dictionary with ball x, y position
    ball_direction = models.JSONField(default=dict)  # Dictionary with ball x, y velocity/direction
    
    def get_invite_link(self):
        return f"/pong-ws/{self.id}/"
        # return f"/pong/{self.id}/"

    def get_game_state(self):
        # Use hard-coded default values instead of canvas dimensions
        default_ball_pos = {"x": 400, "y": 200}  # Half of canvas width/height
        default_ball_dir = {"dx": 3, "dy": 3}
        
        return {
            'player1': self.player1.username,
            'player2': self.player2.username if self.player2 else None,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'player1_paddle': self.player1_paddle,
            'player2_paddle': self.player2_paddle,
            'ball_position': self.ball_position if self.ball_position else default_ball_pos,
            'ball_direction': self.ball_direction if self.ball_direction else default_ball_dir,
        }

    def update_game_state(self, player1_paddle, player2_paddle, ball_position, ball_direction):
        self.player1_paddle = player1_paddle
        self.player2_paddle = player2_paddle
        self.ball_position = ball_position
        self.ball_direction = ball_direction
        self.save()


