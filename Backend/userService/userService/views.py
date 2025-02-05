# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:10:18 by ipetruni          #+#    #+#              #
#    Updated: 2025/02/05 12:11:01 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import generics
from .serializers import UserSerializer, UserProfileSerializer, FriendRequestSerializer
from .models import Profile, Friendship, Chat, Message
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.messages.api import *  # NOQA
from django.contrib.messages.constants import *  # NOQA
from django.contrib.messages.storage.base import Message  # NOQA
from django.views.generic import DetailView 
import json
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.auth import get_user_model
import logging

from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from .models import Chat, Profile, Friendship
from .serializers import ChatSerializer, ChatListSerializer
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

logger = logging.getLogger(__name__)

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


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        print("Raw request data:", request.body)
        username = request.data.get("username")
        password = request.data.get("password")
        print(f"Username: {username}, Password length: {len(password) if password else 0}")

        if not username or not password:
            return Response(
                {"message": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        print('Request received:', request.data)
        
        if user:
            # Get or create token using correct import
            token, created = Token.objects.get_or_create(user=user)
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
            
            return Response({
                'token': token.key,
                'user': user_data
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"message": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]  # First: Validates authToken
    permission_classes = [IsAuthenticated]         # Then: Checks if identified user has access

    def get(self, request):
        try:
            logger.debug(f"Fetching profile for user: {request.user.username}")
            
            # Use get_object_or_404 instead of direct get()
            user_profile = get_object_or_404(Profile, user=request.user)
            
            # Fetch friends
            friends = user_profile.get_friends()
            
            # Serialize data
            serializer_context = {"request": request}
            friends_data = UserProfileSerializer(friends, many=True, context=serializer_context).data
            profile_data = UserProfileSerializer(user_profile, context=serializer_context).data
            profile_data['friends'] = friends_data
            
            logger.debug(f"Successfully retrieved profile for user: {request.user.username}")
            return Response(profile_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return Response(
                {"error": "Failed to retrieve profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """Handle avatar deletion"""
        try:
            user_profile = request.user.profile
            
            if not user_profile.avatar:
                return Response(
                    {"message": "Already using default avatar"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_profile.avatar.delete(save=False)
            user_profile.avatar = None
            user_profile.save()
            
            logger.info(f"Reset avatar to default for user {request.user.username}")
            
            serializer = UserProfileSerializer(user_profile, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Avatar deletion error: {str(e)}")
            return Response(
                {"message": "Failed to delete avatar"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user_profile = request.user.profile
        data = request.data

        if 'display_name' in data:
            display_name = data['display_name'].strip()

            if Profile.objects.filter(display_name=display_name).exclude(user=request.user).exists():
                return Response({"message": "Display name is already taken"}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.display_name = display_name
            logger.info(f"Updated display name for user {request.user.username}")
            
        if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                
                # Validate file type
                if not avatar.content_type.startswith('image/'):
                    return Response(
                        {"message": "Invalid file type. Please upload an image"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate file size (5MB limit)
                if avatar.size > 5 * 1024 * 1024:
                    return Response(
                        {"message": "File too large. Maximum size is 5MB"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Delete old avatar if exists
                if user_profile.avatar:
                    user_profile.avatar.delete(save=False)
                
                user_profile.avatar = avatar
                logger.info(f"Updated avatar for user {request.user.username}")

        user_profile.save()
        
        # Return updated profile data
        serializer = UserProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
class SearchProfilesView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        logger.debug(f"Search query: {query}")
        
        if not query:
            return Response([])

        try:
            current_user = request.user
            
            # Find users matching search criteria and apply filters
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(profile__display_name__icontains=query)
            ).exclude(
                Q(id=current_user.id) |  # Exclude current user
                Q(profile__blocked_users=current_user)  # Exclude users who blocked current user
            )

            # Get profiles for matched users
            profiles = Profile.objects.filter(user__in=users)
            
            logger.debug(f"Found {profiles.count()} profiles before block check")
            context = {"request": request}
            serializer = UserProfileSerializer(profiles, many=True, context=context)
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@permission_classes([IsAuthenticated])
class BlockUserView(APIView):

    def post(self, request, user_id):
        try:
            user_to_block = get_object_or_404(User, id=user_id)
            request.user.profile.blocked_users.add(user_to_block)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, user_id):
        try:
            user_to_unblock = get_object_or_404(User, id=user_id)
            request.user.profile.blocked_users.remove(user_to_unblock)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([IsAuthenticated])
class AddFriendView(APIView):
    def post(self, request):
        from_profile = request.user.profile
        to_profile_id = request.data.get('friend_profile_id')  # Adjust key as per frontend

        if not to_profile_id:
            return Response({'error': 'Friend profile ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_profile = Profile.objects.get(id=to_profile_id)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if friendship already exists or if there's a pending request
        existing_friendship = Friendship.objects.filter(
            Q(from_profile=from_profile, to_profile=to_profile) |
            Q(from_profile=to_profile, to_profile=from_profile)
        ).first()

        if existing_friendship:
            if existing_friendship.status == 'accepted':
                return Response({'message': 'You are already friends'}, status=status.HTTP_200_OK)
            elif existing_friendship.status == 'pending':
                return Response({'message': 'Friend request already sent or received'}, status=status.HTTP_200_OK)

        # Create a new friendship request
        Friendship.objects.create(from_profile=from_profile, to_profile=to_profile, status='pending')

        # Send a WebSocket notification to the recipient
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{to_profile.user.id}",
            {
                'type': 'send_notification',
                'message': {
                    'type': 'friend_request',
                    'from_user_id': from_profile.user.id,
                    'from_user_name': from_profile.display_name,
                    'from_user_avatar': from_profile.avatar.url if from_profile.avatar else '',
                },
            }
        )

        return Response({'message': 'Friend request sent successfully'}, status=status.HTTP_201_CREATED)

@permission_classes([IsAuthenticated])
class IncomingFriendRequestsView(APIView):
    def get(self, request):
        try:
            user_profile = request.user.profile
            incoming_requests = Friendship.objects.filter(
                to_profile=user_profile,
                status='pending'
            ).select_related('from_profile')

            serializer = FriendRequestSerializer(incoming_requests, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching friend requests: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@permission_classes([IsAuthenticated])
class DeclineFriendRequestView(APIView):
    def post(self, request):
        to_profile = request.user.profile
        from_user_id = request.data.get('from_user_id')
        
        # Add logging
        logger.debug(f"Decline friend request: from_user_id={from_user_id}")

        if not from_user_id:
            return Response({'error': 'From user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find profile by user ID first
            from_profile = Profile.objects.select_related('user').get(user_id=from_user_id)
            logger.debug(f"Found profile: {from_profile.display_name}")

        except Profile.DoesNotExist:
            logger.error(f"Profile not found for user_id: {from_user_id}")
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            friendship = Friendship.objects.get(
                from_profile=from_profile, 
                to_profile=to_profile, 
                status='pending'
            )
            friendship.delete()

            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{from_profile.user.id}",
                {
                    'type': 'send_notification',
                    'message': {
                        'type': 'friend_request_declined',
                        'user_id': to_profile.user.id,
                        'user_name': to_profile.display_name,
                        'user_avatar': to_profile.avatar.url if to_profile.avatar else '',
                    },
                }
            )

            return Response({'message': 'Friend request declined'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            logger.error(f"Friendship not found between {to_profile.id} and {from_profile.id}")
            return Response({'error': 'Friend request not found'}, status=status.HTTP_400_BAD_REQUEST)
        
@permission_classes([IsAuthenticated])
class AcceptFriendRequestView(APIView):
    def post(self, request):
        to_profile = request.user.profile
        from_user_id = request.data.get('from_user_id')
        
        # Add logging
        logger.debug(f"Accept friend request: from_user_id={from_user_id}")

        if not from_user_id:
            return Response({'error': 'From user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find profile by user ID first
            from_profile = Profile.objects.select_related('user').get(user_id=from_user_id)
            logger.debug(f"Found profile: {from_profile.display_name}")

        except Profile.DoesNotExist:
            logger.error(f"Profile not found for user_id: {from_user_id}")
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            friendship = Friendship.objects.get(
                from_profile=from_profile, 
                to_profile=to_profile, 
                status='pending'
            )
            friendship.status = 'accepted'
            friendship.save()

            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{from_profile.user.id}",
                {
                    'type': 'send_notification',
                    'message': {
                        'type': 'friend_request_accepted',
                        'user_id': to_profile.user.id,
                        'user_name': to_profile.display_name,
                        'user_avatar': to_profile.avatar.url if to_profile.avatar else '',
                    },
                }
            )

            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            logger.error(f"Friendship not found between {to_profile.id} and {from_profile.id}")
            return Response({'error': 'Friend request not found'}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class RemoveFriendView(APIView):
    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        friend_profile_id = request.data.get('friend_profile_id')

        try:
            friend_profile = Profile.objects.get(id=friend_profile_id)
            friendship = Friendship.objects.filter(
                (Q(from_profile=user_profile, to_profile=friend_profile) |
                 Q(from_profile=friend_profile, to_profile=user_profile)),
                status='accepted'
            ).first()

            if not friendship:
                return Response({"message": "Friendship not found"}, status=status.HTTP_404_NOT_FOUND)

            friendship.delete()

            # Send a WebSocket notification to the friend
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_profile.user.id}",
                {
                    'type': 'send_notification',
                    'message': {
                        'type': 'friend_removed',
                        'user_id': user_profile.user.id,
                        'user_name': user_profile.display_name,
                        'user_avatar': user_profile.avatar.url if user_profile.avatar else '',
                    },
                }
            )

            return Response({"message": "Friend removed successfully"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_profile = request.user.profile
            user_profile.is_online = False
            user_profile.save()

            # Notify friends that the user is offline
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{user_profile.user.id}",
                {
                    'type': 'send_notification',
                    'message': {
                        'type': 'friend_status',
                        'user_id': user_profile.user.id,
                        'status': 'offline',
                    },
                }
            )

            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            return Response({"message": "Logout not successful"}, status=status.HTTP_200_OK)

class ChatListView(generics.ListAPIView):
    serializer_class = ChatListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(participant1=user) | Chat.objects.filter(participant2=user)
    
class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user1 = self.request.user
        user2 = User.objects.get(pk=self.kwargs['pk'])
        return (Chat.objects.filter(participant1=user1, participant2=user2) | Chat.objects.filter(participant1=user2, participant2=user1)).first()