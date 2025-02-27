from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('game_invite', 'Game Invitation'),
        ('game_accepted', 'Game Accepted'),
        ('game_declined', 'Game Declined'),
        ('friend_request', 'Friend Request'),
        ('friend_accepted', 'Friend Request Accepted'),
        ('friend_declined', 'Friend Request Declined'),
        ('friend_removed', 'Friend Removed'),
        ('chat_message', 'Chat Message'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.JSONField()  # Store all notification data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username} from {self.sender.username}"