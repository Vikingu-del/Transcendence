from rest_framework import serializers
from .models import Notification

# Fix the method in serializers.py
class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content', 'created_at', 'is_read', 'sender_name']
    
    def get_sender_name(self, obj):  # Must have 'obj' parameter
        if obj.sender and hasattr(obj.sender, 'profile'):
            return obj.sender.profile.display_name
        return obj.sender.username if obj.sender else 'Unknown'