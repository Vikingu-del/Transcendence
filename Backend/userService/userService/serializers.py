# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:54 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/21 12:38:16 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
import random

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password1']

    def save(self, **kwargs):
        # Get user credentials from validated data
        username = self.validated_data['username']
        password = self.validated_data['password1']

        # Create the user
        user = User.objects.create_user(username=username, password=password)

        # Generate a unique display name
        base_display_name = "Player"
        display_name = f"{base_display_name}{random.randint(100000, 999999)}"

        # Ensure the display name is unique
        while Profile.objects.filter(display_name=display_name).exists():
            display_name = f"{base_display_name}{random.randint(100000, 999999)}"

        # Create the user profile
        Profile.objects.create(user=user, display_name=display_name, avatar=None)
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['display_name', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and obj.avatar.url:
            return f"{request.scheme}://{request.get_host()}:{request.get_port()}{obj.avatar.url}"
        return f"{request.scheme}://{request.get_host()}:{request.get_port()}/media/static/default.png"

