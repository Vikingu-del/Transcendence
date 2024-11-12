from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        logger.debug("Received registration data: %s", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        logger.debug("Registration errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)
        return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Logout not successful"}, status=status.HTTP_200_OK)
    
@method_decorator(csrf_exempt, name='dispatch')
class FriendView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            friend_username = request.data.get("friend_username")
            try:
                friend_user = User.objects.get(username=friend_username)
                Friend.objects.create(user=request.user, friend=friend_user)
                return Response({"message": "Friend added"}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            friends = Friend.objects.filter(user=request.user)
            serializer = FriendSerializer(friends, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class MatchHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            match_history = MatchHistory.objects.filter(user=request.user)
            serializer = MatchHistorySerializer(match_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)