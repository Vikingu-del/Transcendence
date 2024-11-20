# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    serializers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:54 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/20 10:35:59 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password1']

    def save(self, **kwargs):
        username = self.validated_data['username']
        password = self.validated_data['password1']

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, display_name="Player", avatar=None)
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

