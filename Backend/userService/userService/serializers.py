# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:54 by ipetruni          #+#    #+#              #
#    Updated: 2025/03/02 15:40:10 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Friendship
from django.db.models import Q
from django.conf import settings
import random

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self, **kwargs):
        username = self.validated_data['username']
        password = self.validated_data['password1']

        user = User.objects.create_user(username=username, password=password)

        base_display_name = "Player"
        display_name = f"{base_display_name}{random.randint(100000, 999999)}"

        while Profile.objects.filter(display_name=display_name).exists():
            display_name = f"{base_display_name}{random.randint(100000, 999999)}"

        # Create profile with default avatar
        Profile.objects.create(
            user=user,
            display_name=display_name,
            avatar=settings.DEFAULT_AVATAR_PATH
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField()
    friend_request_status = serializers.SerializerMethodField()
    requested_by_current_user = serializers.SerializerMethodField()
    isBlocked = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'display_name', 'avatar', 'is_online', 'friends',
                 'friend_request_status', 'requested_by_current_user', 'isBlocked', 'language']

    def get_avatar(self, obj):
        return obj.get_avatar_url()
    
    def get_friends(self, obj):
        return obj.get_friends()
    
    def get_is_friend(self, obj):
        user = self.context['request'].user
        return Friendship.objects.filter(
            (Q(from_profile=user.profile) & Q(to_profile=obj) & Q(status='accepted')) |
            (Q(from_profile=obj) & Q(to_profile=user.profile) & Q(status='accepted'))
        ).exists()

    def get_friend_request_status(self, obj):
        user = self.context['request'].user
        friendship = Friendship.objects.filter(
            (Q(from_profile=user.profile) & Q(to_profile=obj)) |
            (Q(from_profile=obj) & Q(to_profile=user.profile))
        ).first()
        return friendship.status if friendship else None

    def get_requested_by_current_user(self, obj):
        user = self.context['request'].user
        return Friendship.objects.filter(from_profile=user.profile, to_profile=obj, status='pending').exists()

    def get_blocked_users(self, obj):
        return obj.blocked_users.values_list('id', flat=True)
    
    def get_isBlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.profile.blocked_users.filter(id=obj.user.id).exists()
        return False

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'status', 'created']
        
    def get_from_user(self, obj):
        return {
            'id': obj.from_profile.user.id,
            'display_name': obj.from_profile.display_name,
            'avatar': obj.from_profile.get_avatar_url(),
            'is_online': obj.from_profile.is_online
        }