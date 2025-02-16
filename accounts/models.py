from django.db import models
import pyotp
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	totp_secret = models.CharField(max_length=32, blank=True, null=True) #add a TOTP table

	def generate_totp_secret(self):
		self.totp_secret = pyotp.random_base32()
		self.save()
