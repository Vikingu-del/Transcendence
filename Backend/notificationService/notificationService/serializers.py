from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content', 'created_at', 'is_read', 'sender_name']
    
    def get_sender_name(self, obj):
        return obj.sender.username