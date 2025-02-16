from django.contrib import admin
from .models import GameSession

class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'player1_score', 'player2_score', 'winner', 'created_at', 'ended_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'ended_at')
    search_fields = ('player1__username', 'player2__username')
    ordering = ('-ended_at',)

admin.site.register(GameSession, GameSessionAdmin)
