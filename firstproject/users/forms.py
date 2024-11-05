from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Friend

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'display_name', 'avatar', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'display_name', 'avatar')
        
# class Friend(models.Model):
#     user = models.ForeignKey(CustomUser, related_name='friends', on_delete=models.CASCADE)
#     friend = models.ForeignKey(CustomUser, related_name='friend_of', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.user.username} is friends with {self.friend.username}'