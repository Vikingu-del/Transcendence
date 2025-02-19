# from django.db import models
# from django.contrib.auth.models import User

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     is_online = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user.username}'s Profile"

# class ChatMessage(models.Model):
#     sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     read = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Message from {self.sender.user.username} to {self.receiver.user.username} at {self.timestamp}"

# class BlockList(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='blocking')
#     blocked_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='blocked_by')

#     class Meta:
#         unique_together = ('user', 'blocked_user')  # Ensure each block relationship is unique

#     def __str__(self):
#         return f"{self.user.user.username} blocked {self.blocked_user.user.username}"

# class GameInvite(models.Model):
#     PENDING = 'Pending'
#     ACCEPTED = 'Accepted'
#     DECLINED = 'Declined'
    
#     INVITE_STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (ACCEPTED, 'Accepted'),
#         (DECLINED, 'Declined'),
#     ]
    
#     sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_invites')
#     receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_invites')
#     invite_status = models.CharField(max_length=10, choices=INVITE_STATUS_CHOICES, default=PENDING)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Game invite from {self.sender.user.username} to {self.receiver.user.username} - Status: {self.invite_status}"

# class TournamentWarning(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tournament_warnings')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Tournament warning from {self.user.user.username} at {self.timestamp}"

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfileModel(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=100)
    online_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"({self.thread_name}) {self.sender}: {self.message}")
    
class ChatNotification(models.Model):
    chat = models.ForeignKey(to=ChatModel, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
