import requests
from django.shortcuts import redirect
import requests.cookies
from .authentication import CookieJWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

def refresh_tokens(request):
	refresh_token = request.COOKIES.get('refresh_token')
	if not refresh_token:
		return None

	response = requests.post(
		'http://127.0.0.1:8000/accounts/api/token/refresh',
		data={'refresh': refresh_token}
	)
 
	if response.status_code == 200:
		return response.json()
	return None

def is_token_valid(request):
	authentication = CookieJWTAuthentication()
	try:
		result = authentication.authenticate(request)
		if result is None:
			return False, None
		user, _ = result
		return True, user
	except AuthenticationFailed as e:
		if "Token has expired" in str(e):
			return False, None
		return False, None

def store_tokens_in_cookies(tokens, request):
		response = redirect(request.path)
		if 'access' in tokens:
			response.set_cookie('access_token', tokens['access'], httponly=True, secure=True, samesite='Lax')
		refresh_token = request.COOKIES.get('refresh_token')
		if refresh_token:
			response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Lax')
		return response