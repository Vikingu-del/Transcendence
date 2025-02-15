import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError  # ✅ Correct imports
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import User


class CookieJWTAuthentication(BaseAuthentication):
	def authenticate(self, request):
		token = request.COOKIES.get('access_token')
		if not token:
			return None

		try:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
			user = User.objects.get(id=payload["user_id"])
			return (user, None)
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Token has expired")
		except jwt.InvalidTokenError:
			raise AuthenticationFailed("Invalid Token")
		except User.DoesNotExist:
			raise AuthenticationFailed("User not found")