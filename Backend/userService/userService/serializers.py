from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Friend, MatchHistory

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password1']

    def save(self, **kwargs):
        username = self.validated_data['username']
        password = self.validated_data['password1']
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, display_name=username)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'avatar', 'wins', 'losses', 'match_history']

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['user', 'friend']

class MatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['user', 'opponent', 'date', 'result']