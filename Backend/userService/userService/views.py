# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:10:18 by ipetruni          #+#    #+#              #
#    Updated: 2025/02/18 20:40:29 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
import logging
from .serializers import UserProfileSerializer, FriendRequestSerializer
from .models import Profile, Friendship, UserJWTToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)

class SyncTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        logger.debug(f"Received sync token request: {request.data}")
        
        # Verify internal API key
        if request.headers.get('Internal-API-Key') != settings.INTERNAL_API_KEY:
            logger.error("Invalid Internal API key")
            return Response(
                {'error': 'Invalid API key'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        token = request.data.get('token')
        username = request.data.get('username')

        if not all([user_id, token, username]):
            logger.error("Missing required fields")
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                id=user_id,
                defaults={'username': username}
            )

            # Create or update profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': username,
                    'avatar': 'default.png'
                }
            )

            logger.info(f"Successfully synced token for user {username}")
            return Response({
                'status': 'success',
                'user_id': user.id,
                'profile_id': profile.id
            })

        except Exception as e:
            logger.error(f"Sync token error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Token synchronization failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Log the token for debugging
            auth_header = request.headers.get('Authorization', '')
            logger.debug(f"Auth header: {auth_header}")
            
            # Get profile directly from authenticated user
            profile = Profile.objects.get(user=request.user)
            
            data = {
                'id': profile.id,
                'display_name': profile.display_name,
                'avatar': profile.get_avatar_url(),
                'is_online': profile.is_online,
                'friends': []
            }
            
            return Response(data)
            
        except Profile.DoesNotExist:
            logger.error(f"Profile not found for user {request.user.id}")
            return Response(
                {"detail": "Profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            profile = request.user.profile
            
            if not profile.avatar:
                return Response(
                    {"message": "Already using default avatar"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Use the new delete_avatar method
            profile.delete_avatar()
            
            serializer = UserProfileSerializer(profile, context={"request": request})
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Avatar deletion error: {str(e)}")
            return Response(
                {"message": "Failed to delete avatar"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        data = request.data
        try:
            # Handle display name update
            if 'display_name' in data:
                new_display_name = data['display_name'].strip()
                
                if Profile.objects.filter(display_name=new_display_name).exclude(user=request.user).exists():
                    return Response(
                        {"error": "Display name already in use"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                profile.display_name = new_display_name
                profile.save()
                
            # Handle avatar update
            elif 'avatar' in request.FILES:
                avatar = request.FILES['avatar']

                if not avatar.content_type.startswith('image'):
                    return Response(
                        {"error": "Invalid image format"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if avatar.size > 5 * 1024 * 1024:  # 5MB limit
                    return Response(
                        {"error": "Image size too large"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if profile.avatar and profile.avatar.name != settings.DEFAULT_AVATAR_PATH:
                    # I dont want to delete phisically the file
                    profile.delete_avatar() # here was the problem before you were using profile.avatar.delete()
                    
                    
                
                profile.avatar = avatar
                profile.save()
                logger.info(f"Updated avatar for user {request.user.username}")

            serializer = UserProfileSerializer(profile, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

class AddFriendView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from_profile = request.user.profile
        to_profile_id = request.data.get('friend_profile_id')

        # Add debug logging
        logger.debug(f"Add friend request: from_profile={from_profile.id}, to_profile_id={to_profile_id}")

        if not to_profile_id:
            return Response(
                {'error': 'Friend profile ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            to_profile = Profile.objects.get(id=to_profile_id)
            
            # Check if users are already friends
            existing_friendship = Friendship.objects.filter(
                Q(from_profile=from_profile, to_profile=to_profile) |
                Q(from_profile=to_profile, to_profile=from_profile)
            ).first()

            if existing_friendship:
                logger.debug(f"Existing friendship found: status={existing_friendship.status}")
                if existing_friendship.status == 'accepted':
                    return Response(
                        {'message': 'Already friends'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {'message': 'Friend request already pending'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create new friendship request
            friendship = Friendship.objects.create(
                from_profile=from_profile,
                to_profile=to_profile,
                status='pending'
            )

            logger.debug(f"Created new friendship: id={friendship.id}")
            return Response(
                {'message': 'Friend request sent successfully'}, 
                status=status.HTTP_201_CREATED
            )

        except Profile.DoesNotExist:
            logger.error(f"Profile not found: id={to_profile_id}")
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating friend request: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
