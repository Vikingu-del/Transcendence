from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken # Eric Added
from rest_framework_simplejwt.authentication import JWTAuthentication # Eric Added
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
import requests
from django.conf import settings
import logging
from .serializers import RegistrationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from .qrcode import generateQRCode
from .models import UserTOTP
import pyotp

logger = logging.getLogger(__name__)

# CreateAPIView provides:
# Built-in creation behavior
# Serializer handling
# Automatic response formatting
# Model instance creation
class RegisterView(generics.CreateAPIView):
	serializer_class = RegistrationSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			# Create the user without token
			user = serializer.save()
			totp_secret = pyotp.random_base32()

			user_totp, created = UserTOTP.objects.get_or_create(user=user)
			user_totp.totp_secret = totp_secret
			user_totp.save()
			user.save()
			qr_code = generateQRCode(user.email, totp_secret)
			return Response({
				'message': 'Registration successful',
				'user': serializer.data,
				'qr_code': f"data:image/png;base64,{qr_code}",
			}, status=status.HTTP_201_CREATED)
		return Response({
			"error": "Registration failed", 
			"details": serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)


# APIView is used when you want:
# More control over the HTTP methods
# Custom authentication logic
# No model-based operations
# Simpler request handling
class LoginView(APIView):
	def post(self, request):
		try:
			username = request.data.get("username")
			password = request.data.get("password")
			otp = request.data.get("otp")

			user = authenticate(username=username, password=password)
			
			if user:
				try:
					user_totp = UserTOTP.objects.get(user__username=username)
					totp_secret = user_totp.totp_secret
					totp = pyotp.TOTP(totp_secret)
					if not totp.verify(otp):
						return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
				except UserTOTP.DoesNotExist:
					return Response({'error': 'User Not found'}, status=status.HTTP_404_NOT_FOUND)

				# Generate JWT token
				refresh = RefreshToken.for_user(user)
				access_token = str(refresh.access_token)
				
				# Sync token with user service
				response = requests.post(
					f"{settings.USER_SERVICE_URL}/api/user/sync-token/",
					json={
						'user_id': user.id,
						'token': access_token,
						'username': user.username
					},
					headers={
						'Internal-API-Key': settings.INTERNAL_API_KEY,
						'Content-Type': 'application/json'
					}
				)
				
				if not response.ok:
					logger.error(f"Failed to sync token: {response.text}")
					return Response({
						'error': 'Failed to sync token'
					}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

				return Response({
					'token': access_token,
					'refresh': str(refresh),
					'user': {
						'id': user.id,
						'username': user.username
					}
				})
			
			return Response({
				'error': 'Invalid credentials'
			}, status=status.HTTP_401_UNAUTHORIZED)
			
		except Exception as e:
			logger.error(f"Login error: {str(e)}", exc_info=True)
			return Response({
				'error': 'Authentication failed'
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		try:
			# Set user offline
			profile = request.user.profile
			profile.is_online = False
			profile.save()

			# Notify other users about offline status
			channel_layer = get_channel_layer()
			async_to_sync(channel_layer.group_send)(
				f"user_{request.user.id}",
				{
					"type": "friend_status",
					"message": {
						"type": "friend_status",
						"user_id": request.user.id,
						"status": "offline"
					}
				}
			)

			# Delete auth token
			# request.user.auth_token.delete() // For JWT, we don't need to delete the token as they are stateless instead the might want to add the toke to a blacklist or let it expire naturyally
			
			return Response({"message": "Successfully logged out."}, 
						status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"error": str(e)}, 
						status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
	def post(self, request):
		try:
			refresh = request.data.get('refresh')
			token = RefreshToken(refresh)
			print(f'token: {token}')
			return Response({'access': str(token.access_token)})
		except Exception as e:
			logger.error(f"Token refresh error: {str(e)}", exc_info=True)
			return Response({'error': 'Token refresh failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ValidateTokenView(APIView):
	def get(self, request):
		try:
			# Get token from header
			auth_header = request.headers.get('Authorization')
			if not auth_header or not auth_header.startswith('Bearer '):
				return Response({'error': 'No token provided'}, status=status.HTTP_401_UNAUTHORIZED)
			
			token = auth_header.split(' ')[1]
			
			# Validate token
			AccessToken(token)
			
			return Response({'valid': True}, status=status.HTTP_200_OK)
			
		except TokenError:
			return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
		except Exception as e:
			logger.error(f"Token validation error: {str(e)}", exc_info=True)
			return Response({'error': 'Validation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateQRCodeView(APIView):
	def post(self, request):
		try:
			username = request.data.get("username")
			user = User.objects.get(username=username)
			user_totp = UserTOTP.objects.get(user=user)
			qr_code = generateQRCode(user.email, user_totp.totp_secret)
			return Response({
				'qr_code': f"Data:image/png;base64,{qr_code}"},
				status=status.HTTP_200_OK,
			)
		except User.DoesNotExist:
			return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
		except UserTOTP.DoesNotExist:
			return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
		except Exception as e:
			logger.error(f"QR code generation failed: {str(e)}")
			return Response({
				'error': 'QR code generation failed'
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)