from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import RegisterForm, LoginForm
import requests

# Create your views here.
def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			print (f"Created user {form.cleaned_data.get('username')}")
			return redirect('login')
	else:
		form = RegisterForm()
	return render(request, 'register.html', {'form': form})

def login_view(request):
	form = LoginForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				response = requests.post(
					'http://127.0.0.1:8000/accounts/api/token',
					json={'username':username, 'password':password},
				)
				if response.status_code == 200:
					tokens = response.json()
					json_response = JsonResponse({'success': True})
					json_response.set_cookie('access_token', tokens['access'], httponly=True, secure=True, samesite='Lax')
					json_response.set_cookie('refresh_token', tokens['refresh'], httponly=True, secure=True, samesite='Lax')
					return redirect('home')
				else:
					return JsonResponse({'error': 'Failed to obtain JWT tokens'}, status=400)
			else:
				return JsonResponse({'error': 'Invalid credentials'}, status=400)
		else:
			form = LoginForm()
	return render(request, 'login.html', {'form': form})

def home(request):
	return render(request, 'home.html')