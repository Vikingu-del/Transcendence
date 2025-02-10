from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Chat, Message
from django.db.models import Q
import random


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'created_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = instance.sender.id  # Return numeric ID instead of username
        return data


class ChatSerializer(serializers.ModelSerializer):
    participant2 = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
            model = Chat
            fields = ['id', 'participant1', 'participant2', 'messages']
    
    def get_participant2(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        target_user = obj.participant2 if obj.participant1 == request.user else obj.participant1
        return {
            'id': target_user.id,
            'username': target_user.username,
            'profile_image': target_user.profile.avatar.url if hasattr(target_user.profile, 'avatar') and target_user.profile.avatar else None
        }


class ChatListSerializer(serializers.ModelSerializer):
    participant2 = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'participant2', 'last_message']
    
    def get_participant2(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        target_user = obj.participant2 if obj.participant1 == request.user else obj.participant1
        return {
            'id': target_user.id,
            'username': target_user.username,
            'profile_image': target_user.profile.avatar.url if hasattr(target_user.profile, 'avatar') and target_user.profile.avatar else None
        }
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'text': last_msg.text,
                'created_at': last_msg.created_at,
                'sender': last_msg.sender.username
            }
        return None