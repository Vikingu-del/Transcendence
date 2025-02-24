from django.db import models
from django.contrib.auth.models import User

class UserTOTP(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='totp')
	totp_secret = models.CharField(max_length=6, blank=True, null=True)

	def __str__(self):
		return f"TOTP Secret for {self.user.username}"