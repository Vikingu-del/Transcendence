from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1']

    def save(self, **kwargs):
        username = self.validated_data['username']
        email = self.validated_data['email']
        password = self.validated_data['password1']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return user