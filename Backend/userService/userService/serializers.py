from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Friend, MatchHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'display_name', 'avatar', 'wins', 'losses', 'match_history']

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['user', 'friend']

class MatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['user', 'opponent', 'date', 'result']