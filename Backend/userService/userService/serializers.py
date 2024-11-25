# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:54 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/21 14:20:09 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
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
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['display_name', 'avatar', 'friends']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and obj.avatar.url:
            return f"{request.scheme}://{request.get_host()}:{request.get_port()}{obj.avatar.url}"
        return f"{request.scheme}://{request.get_host()}:{request.get_port()}/media/static/default.png"

    def get_friends(self, obj):
        friends = obj.friends.all()
        return UserProfileSerializer(friends, many=True, context=self.context).data