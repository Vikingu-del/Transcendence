# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:10:18 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/21 13:28:24 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import UserSerializer, UserProfileSerializer
from .models import Profile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        logger.debug("Received registration data: %s", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        
        logger.debug("Registration errors: %s", serializer.errors)
        return Response({"error": "Registration failed", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"message": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        
        return Response(
            {"message": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user_profile = Profile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        data = request.data

        if 'avatar' in data:
            user_profile.avatar = data['avatar']
        
        if 'display_name' in data:
            user_profile.display_name = data['display_name']

        user_profile.save()
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Logout not successful"}, status=status.HTTP_200_OK)
