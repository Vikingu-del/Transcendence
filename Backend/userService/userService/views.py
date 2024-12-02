# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:10:18 by ipetruni          #+#    #+#              #
#    Updated: 2024/12/02 15:42:06 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import UserSerializer, UserProfileSerializer
from .models import Profile, Friendship
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
        friends = user_profile.get_friends()
        friends_data = UserProfileSerializer(friends, many=True, context={"request": request}).data
        profile_data = UserProfileSerializer(user_profile, context={"request": request}).data
        profile_data['friends'] = friends_data
        return Response(profile_data)

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

class SearchProfilesView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        return Profile.objects.filter(display_name__icontains=search_query)

class AddFriendView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        friend_profile_id = request.data.get('friend_profile_id')

        try:
            friend_profile = Profile.objects.get(id=friend_profile_id)
            if Friendship.objects.filter(from_profile=user_profile, to_profile=friend_profile).exists():
                return Response({"message": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
            Friendship.objects.create(from_profile=user_profile, to_profile=friend_profile, status='pending')

            # Send notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_profile.user.id}",
                {
                    "type": "send_notification",
                    "message": {"type": "friend_request", "from": user_profile.display_name}
                }
            )

            return Response({"message": "Friend request sent successfully"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"message": "Friend profile not found"}, status=status.HTTP_404_NOT_FOUND)

class IncomingFriendRequestsView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        incoming_requests = Friendship.objects.filter(to_profile=user_profile, status='pending')
        serializer = UserProfileSerializer([req.from_profile for req in incoming_requests], many=True, context={"request": request})
        return Response(serializer.data)

class DeclineFriendRequestView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        friend_profile_id = request.data.get('friend_profile_id')

        try:
            friend_profile = Profile.objects.get(id=friend_profile_id)
            friendship = Friendship.objects.get(from_profile=friend_profile, to_profile=user_profile, status='pending')
            friendship.delete()
            return Response({"message": "Friend request declined"}, status=status.HTTP_200_OK)
        except (Profile.DoesNotExist, Friendship.DoesNotExist):
            return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

class AcceptFriendRequestView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        friend_profile_id = request.data.get('friend_profile_id')

        try:
            friend_profile = Profile.objects.get(id=friend_profile_id)
            friendship = Friendship.objects.get(from_profile=friend_profile, to_profile=user_profile, status='pending')
            friendship.status = 'accepted'
            friendship.save()

            # Send notification to the friend
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_profile.user.id}",
                {
                    "type": "send_notification",
                    "message": {"type": "friend_accepted", "from": user_profile.display_name}
                }
            )

            return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
        except (Profile.DoesNotExist, Friendship.DoesNotExist):
            return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

class RemoveFriendView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        friend_profile_id = request.data.get('friend_profile_id')

        try:
            friend_profile = Profile.objects.get(id=friend_profile_id)
            Friendship.objects.filter(
                (Q(from_profile=user_profile) & Q(to_profile=friend_profile)) |
                (Q(from_profile=friend_profile) & Q(to_profile=user_profile))
            ).delete()

            # Send notification to the friend
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_profile.user.id}",
                {
                    "type": "send_notification",
                    "message": {"type": "friend_removed", "from": user_profile.display_name}
                }
            )

            return Response({"message": "Friend removed successfully"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"message": "Friend profile not found"}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Logout not successful"}, status=status.HTTP_200_OK)
