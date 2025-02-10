from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class Chat(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['participant1']),
            models.Index(fields=['participant2'])
        ]
    
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    participant1 = models.ForeignKey(User, related_name='chats1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='chats2', on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        self.id = '_'.join(sorted([str(self.participant1_id), str(self.participant2_id)]))
        super().save(*args, **kwargs)

class Message(models.Model):
    class Meta:
        ordering = ['created_at']
    
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
