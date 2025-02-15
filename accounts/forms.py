from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
	username = forms.CharField(max_length=150, required=True)
	password = forms.CharField(widget=forms.PasswordInput, required=True)