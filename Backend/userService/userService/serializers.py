# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:54 by ipetruni          #+#    #+#              #
#    Updated: 2024/12/03 16:14:54 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Friendship
from django.db.models import Q
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

        Profile.objects.create(user=user, display_name=display_name, avatar=None)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    friend_request_status = serializers.SerializerMethodField()
    requested_by_current_user = serializers.SerializerMethodField()


    class Meta:
        model = Profile
        fields = ['id', 'display_name', 'avatar', 'is_friend', 'friend_request_status', 'requested_by_current_user']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and obj.avatar.url:
            return f"{request.scheme}://{request.get_host()}:{request.get_port()}{obj.avatar.url}"
        return f"{request.scheme}://{request.get_host()}:{request.get_port()}/media/default.png"

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