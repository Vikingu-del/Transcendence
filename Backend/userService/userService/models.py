from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    match_history = models.TextField(blank=True)

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    unique_together = ('user', 'friend')

class MatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opponent = models.ForeignKey(User, related_name='opponent', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=10)  # 'win' or 'loss'