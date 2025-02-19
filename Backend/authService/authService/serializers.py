from rest_framework import serializers
from django.contrib.auth.models import User
import requests
import random
import logging
from django.conf import settings
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password1']
            )

            # Create profile using user service API
            user_service_url = f"{settings.USER_SERVICE_URL}/api/user/profile/"
            profile_data = {
                "user_id": user.id,
                "display_name": f"Player{random.randint(1000, 9999)}"
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                user_service_url,
                json=profile_data,
                headers=headers,
                timeout=settings.USER_SERVICE_TIMEOUT
            )

            if response.status_code != 201:
                user.delete()
                raise serializers.ValidationError(
                    f"Failed to create profile. Status: {response.status_code}"
                )

            return user

        except Exception as e:
            if 'user' in locals():
                user.delete()
            logger.error(f"User creation error: {str(e)}")
            raise serializers.ValidationError(str(e))

class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password1', 'password2')

    def validate_username(self, value):
        # Check minimum length
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        return value

    def validate_password1(self, value):
        # Check minimum length
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long"
            )
        # Check for lowercase
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        # Check for uppercase
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        # Check for digit
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one number"
            )
        # Check for symbol
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in symbols for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one symbol (!@#$%^&*()_+-=[]{}|;:,.<>?)"
            )
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1']
        )
        return user