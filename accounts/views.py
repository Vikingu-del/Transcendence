from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm
from .authentication import CookieJWTAuthentication
from django.contrib import messages
import requests
from .utilities import is_token_valid, refresh_tokens, store_tokens_in_cookies
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.
class RegisterView(FormView):
	template_name = "register.html"
	form_class = RegisterForm
	success_url = '/accounts/login/'

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return super().form_valid(form)

class LoginView(FormView):
	template_name = "login.html"
	form_class = LoginForm
	success_url = '/accounts/home/'

	def form_valid(self, form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(self.request, username=username, password=password)
		if user is not None:
			login(self.request, user)
			response = requests.post(
				'http://127.0.0.1:8000/accounts/api/token',
				json={'username': username, 'password': password},
			)
			if response.status_code == 200:
				tokens = response.json()
				response = HttpResponseRedirect(self.get_success_url())
				response.set_cookie('access_token', tokens['access'], httponly=True, secure=True, samesite='Lax')
				response.set_cookie('refresh_token', tokens['refresh'], httponly=True, secure=True, samesite='Lax')
				return response
			else:
				return JsonResponse({'error': 'Failed to obtain JWT tokens'}, status=400)
		else:
			return JsonResponse({'error': 'Invalid credentials'}, status=400)

class LogoutView(View):
	def get(self, request, *args, **kwargs):
		response = redirect('login')
		response.delete_cookie('access_token')
		response.delete_cookie('refresh_token')
		return response

class HomeView(TemplateView):
	template_name = 'home.html'
	def get(self, request, *args, **kwargs):
		is_valid, user = is_token_valid(request)
		if not is_valid:
			tokens = refresh_tokens(request)
			if tokens:
				return store_tokens_in_cookies(tokens, request)
			return redirect('login')
		return super().get(request, *args, **kwargs)