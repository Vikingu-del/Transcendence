from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import logging
logger = logging.getLogger(__name__)

class Tournament(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting for Players"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(User, related_name="tournaments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    max_players = models.IntegerField(default=4)
    winner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tournaments_won'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def generate_matches(self):
        """Generate tournament matches in a consistent order"""
        try:
            players = list(self.players.all().order_by('id'))
            if len(players) != 4:
                raise ValueError("Tournament requires exactly 4 players")

            # Create semi-finals matches data structure
            semi_finals = [
                {
                    'match_id': f'semi_0',
                    'phase': 'semi-final',
                    'player1': {
                        'id': players[0].id,
                        'username': players[0].username,
                        'display_name': players[0].profile.display_name if hasattr(players[0], 'profile') else players[0].username
                    },
                    'player2': {
                        'id': players[1].id,
                        'username': players[1].username,
                        'display_name': players[1].profile.display_name if hasattr(players[1], 'profile') else players[1].username
                    },
                    'status': 'pending',
                    'winner': None
                },
                {
                    'match_id': f'semi_1',
                    'phase': 'semi-final',
                    'player1': {
                        'id': players[2].id,
                        'username': players[2].username,
                        'display_name': players[2].profile.display_name if hasattr(players[2], 'profile') else players[2].username
                    },
                    'player2': {
                        'id': players[3].id,
                        'username': players[3].username,
                        'display_name': players[3].profile.display_name if hasattr(players[3], 'profile') else players[3].username
                    },
                    'status': 'pending',
                    'winner': None
                }
            ]

            return {
                'semi_finals': semi_finals,
                'final': {
                    'match_id': 'final',
                    'phase': 'final',
                    'player1': None,
                    'player2': None,
                    'status': 'waiting',
                    'winner': None
                },
                'current_phase': 'semi-final'
            }

        except Exception as e:
            logger.error(f"Error generating matches: {str(e)}")
            raise

    def start_tournament(self):
        """Start the tournament and generate initial matches"""
        if self.status != "waiting" or self.players.count() != 4:
            return False

        try:
            matches_data = self.generate_matches()
            self.status = "in_progress"
            self.started_at = timezone.now()
            self.save()
            return matches_data
        except Exception as e:
            logger.error(f"Error starting tournament: {str(e)}")
            return False

    def is_player_enrolled(self, user):
        return self.players.filter(id=user.id).exists()

    def enroll_player(self, user):
        if self.is_player_enrolled(user):
            return False
        if self.players.count() < self.max_players:
            self.players.add(user)
            if self.players.count() == self.max_players:
                self.start_tournament()
            return True
        return False

class TournamentMatch(models.Model):
    MATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player2')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    round_number = models.IntegerField()  # 1 for semi-finals, 2 for finals
    match_order = models.IntegerField()   # Order within the round (0 or 1 for semi-finals)
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    game_session_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['round_number', 'match_order']
        unique_together = ['tournament', 'round_number', 'match_order']

    def __str__(self):
        return f"Match {self.match_order} - Round {self.round_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.winner:
            self.tournament.advance_winners()
            self.tournament.check_tournament_winner()
        
    def all_matches_completed(self):
        """Check if all matches in the current round are completed"""
        return not self.matches.filter(round=self.current_round, status='pending').exists()
    
    def advance_tournament(self):
        """Create matches for the next round based on winners from current round"""
        current_matches = self.matches.filter(round=self.current_round)
        winners = [match.winner for match in current_matches if match.winner]
        
        if len(winners) >= 2:
            self.current_round += 1
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    TournamentMatch.objects.create(
                        tournament=self,
                        round=self.current_round,
                        player1=winners[i],
                        player2=winners[i + 1],
                        match_number=i // 2
                    )