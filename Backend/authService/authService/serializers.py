from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserTOTP
import logging
import pyotp

logger = logging.getLogger(__name__)

class RegistrationSerializer(serializers.ModelSerializer):
	password1 = serializers.CharField(write_only=True)
	password2 = serializers.CharField(write_only=True)
	email = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = ('id', 'email', 'username', 'password1', 'password2')

	def validate_username(self, value):
		# Check minimum length
		if len(value) < 3:
			raise serializers.ValidationError("Username must be at least 3 characters long")
		if User.objects.filter(username=value).exists():
			raise serializers.ValidationError("Username already exists")
		return value

	def validate_password1(self, value):
		# Check minimum length
		if len(value) < 6:
			raise serializers.ValidationError("Password must be at least 6 characters long")
		# Check for lowercase
		if not any(char.islower() for char in value):
			raise serializers.ValidationError("Password must contain at least one lowercase letter")
		# Check for uppercase
		if not any(char.isupper() for char in value):
			raise serializers.ValidationError("Password must contain at least one uppercase letter")
		# Check for digit
		if not any(char.isdigit() for char in value):
			raise serializers.ValidationError("Password must contain at least one number")
		# Check for symbol
		symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
		if not any(char in symbols for char in value):
			raise serializers.ValidationError(f"Password must contain at least one symbol {symbols}")
		return value

	def validate(self, data):
		if data['password1'] != data['password2']:
			raise serializers.ValidationError("Passwords do not match")
		return data


	def create(self, validated_data):
		user = User.objects.create_user(
			username=validated_data['username'],
			email = validated_data['email'],
			password=validated_data['password1'],
		)
		totp_secret = pyotp.random_base32()
		UserTOTP.objects.create(user=user, totp_secret=totp_secret)
		return user

	def to_representation(self, instance):
		return {
			"id": instance.id,
			"username": instance.username
		}