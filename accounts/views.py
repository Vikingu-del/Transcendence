from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from .forms import RegisterForm, LoginForm, OTPForm
from .authentication import CookieJWTAuthentication
from django.contrib import messages
from .models import UserProfile
import requests
from .utilities import is_token_valid, refresh_tokens, store_tokens_in_cookies
from rest_framework.exceptions import AuthenticationFailed
import pyotp
import qrcode
import io
from django.urls import reverse_lazy

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
	success_url = '/accounts/2fa/verify/'

	def form_valid(self, form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(self.request, username=username, password=password)
		if user is not None:
			self.request.session["pre_otp_user_id"] = user.id
			self.request.session["pre_otp_password"] = password
			return HttpResponseRedirect(self.get_success_url())
		else:
			form.add_error("username", "Invalid Credentials")
			return self.form_invalid(form)
	# def form_valid(self, form):
	# 	username = form.cleaned_data['username']
	# 	password = form.cleaned_data['password']
	# 	user = authenticate(self.request, username=username, password=password)
	# 	if user is not None:
	# 		login(self.request, user)
	# 		response = requests.post(
	# 			'http://127.0.0.1:8000/accounts/api/token',
	# 			json={'username': username, 'password': password},
	# 		)
	# 		if response.status_code == 200:
	# 			tokens = response.json()
	# 			response = HttpResponseRedirect(self.get_success_url())
	# 			response.set_cookie('access_token', tokens['access'], httponly=True, secure=True, samesite='Lax')
	# 			response.set_cookie('refresh_token', tokens['refresh'], httponly=True, secure=True, samesite='Lax')
	# 			return response
	# 		else:
	# 			print("\n\n\nFAILED TO OBTAIN JWT TOKENS\n\n\n")
	# 			return redirect('login')
	# 	else:
	# 		return redirect('login')

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

class GenerateQRCodeView(View):
	def get(self, request, *args, **kwargs):
		user_profile, created = UserProfile.objects.get_or_create(user=request.user)
		if not user_profile.totp_secret:
			user_profile.generate_totp_secret()

		#generate uri
		otp_uri = pyotp.totp.TOTP(user_profile.totp_secret).provisioning_uri(
			request.user.email, issuer_name="Transcendence"
		)

		#generate QR code
		qr = qrcode.make(otp_uri)
		img_io = io.BytesIO()
		qr.save(img_io, format="PNG")
		img_io.seek(0)
		return HttpResponse(img_io.read(), content_type="image/png")

User = get_user_model()

class VerifyOTPView(FormView):
	template_name = "verify_otp.html"
	form_class = OTPForm
	success_url = "/accounts/home"

	def form_valid(self, form):
		user_id = self.request.session.get("pre_otp_user_id")
		if not user_id:
			return redirect("login")
		user = get_object_or_404(User, id=user_id)
		user_profile = user.userprofile
		otp_code = form.cleaned_data['otp']
		totp = pyotp.TOTP(user_profile.totp_secret)
		if totp.verify(otp_code):
			login(self.request, user)
			print(user.username)
			response = requests.post(
				"http://127.0.0.1:8000/accounts/api/token",
				json={'username':user.username, 'password': self.request.session.get("pre_otp_password")}
			)
			if response.status_code == 200:
				tokens = response.json()
				res = HttpResponseRedirect(self.get_success_url())
				res.set_cookie('access_token', tokens['access'], httponly=True, secure=True, samesite='Lax')
				res.set_cookie('refresh_token', tokens['refresh'], httponly=True, secure=True, samesite='Lax')

				del self.request.session["pre_otp_user_id"]
				del self.request.session["pre_otp_password"]
				return res
			else:
				print("\n\n\nFAILED TO OBTAIN JWT TOKENS\n\n\n")
				print(response.json())
				return redirect("login")
		else:
			form.add_error("otp", "Invalid OTP, please try again.")
			return self.form_invalid(form)