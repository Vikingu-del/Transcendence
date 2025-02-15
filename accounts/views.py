from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm
from .authentication import CookieJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests

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

class HomeView(TemplateView):
	template_name = 'home.html'
	def get(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return redirect('login')
		return super().get(request, *args, **kwargs)