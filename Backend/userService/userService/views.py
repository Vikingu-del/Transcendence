from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Friend, MatchHistory
from .serializers import UserSerializer, UserProfileSerializer, FriendSerializer, MatchHistorySerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        UserProfile.objects.create(user=user, display_name=request.data.get('display_name'))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

class AddFriendView(APIView):
    def post(self, request, friend_id, *args, **kwargs):
        friend = User.objects.get(id=friend_id)
        user_profile = UserProfile.objects.get(user=request.user)
        Friend.objects.create(user=request.user, friend=friend)
        return Response({"message": "Friend added"}, status=status.HTTP_201_CREATED)

class FriendsListView(generics.ListAPIView):
    serializer_class = FriendSerializer

    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)