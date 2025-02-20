# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    views.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:10:18 by ipetruni          #+#    #+#              #
#    Updated: 2025/02/20 18:26:06 by ipetruni         ###   ########.fr        #
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
import random

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

            base_display_name = "Player"
            display_name = f"{base_display_name}{random.randint(100000, 999999)}"

            while Profile.objects.filter(display_name=display_name).exists():
                display_name = f"{base_display_name}{random.randint(100000, 999999)}"
            
            # Create or update profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': display_name,
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
            # Get profile directly from authenticated user
            profile = Profile.objects.get(user=request.user)
            
            profile.is_online = True
            profile.save(update_fields=['is_online'])
            
            # Use the UserProfileSerializer to serialize the data
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
            
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
                
                if avatar.size > 10 * 1024 * 1024:  # 5MB limit
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


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from_profile = request.user.profile
        to_profile_id = request.data.get('friend_profile_id')

        if not to_profile_id:
            return Response(
                {'error': 'Friend profile ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            to_profile = Profile.objects.get(id=to_profile_id)
            
            existing_friendship = Friendship.objects.filter(
                Q(from_profile=from_profile, to_profile=to_profile) |
                Q(from_profile=to_profile, to_profile=from_profile)
            ).first()

            if existing_friendship:
                if existing_friendship.status == 'accepted':
                    return Response(
                        {'message': 'Already friends'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {'message': 'Friend request already pending'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            friendship = Friendship.objects.create(
                from_profile=from_profile,
                to_profile=to_profile,
                status='pending'
            )

            return Response(
                {'message': 'Friend request sent successfully'}, 
                status=status.HTTP_201_CREATED
            )

        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IncomingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

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

class DeclineFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_profile = request.user.profile
        from_user_id = request.data.get('from_user_id')

        if not from_user_id:
            return Response(
                {'error': 'From user ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from_profile = Profile.objects.get(user_id=from_user_id)
            friendship = Friendship.objects.get(
                from_profile=from_profile, 
                to_profile=to_profile, 
                status='pending'
            )
            friendship.delete()
            return Response(
                {'message': 'Friend request declined'}, 
                status=status.HTTP_200_OK
            )

        except (Profile.DoesNotExist, Friendship.DoesNotExist):
            return Response(
                {'error': 'Friend request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_profile = request.user.profile
        from_user_id = request.data.get('from_user_id')

        if not from_user_id:
            return Response(
                {'error': 'From user ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from_profile = Profile.objects.get(user_id=from_user_id)
            friendship = Friendship.objects.get(
                from_profile=from_profile, 
                to_profile=to_profile, 
                status='pending'
            )
            friendship.status = 'accepted'
            friendship.save()
            return Response(
                {'message': 'Friend request accepted'}, 
                status=status.HTTP_200_OK
            )

        except (Profile.DoesNotExist, Friendship.DoesNotExist):
            return Response(
                {'error': 'Friend request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class RemoveFriendView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Log the request details
            logger.debug(f"Remove friend request: {request.data}")
            logger.debug(f"Auth header: {request.headers.get('Authorization')}")

            user_profile = request.user.profile
            friend_profile_id = request.data.get('friend_profile_id')

            if not friend_profile_id:
                return Response(
                    {"message": "friend_profile_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            friend_profile = Profile.objects.get(id=friend_profile_id)
            friendship = Friendship.objects.filter(
                (Q(from_profile=user_profile, to_profile=friend_profile) |
                 Q(from_profile=friend_profile, to_profile=user_profile)),
                status='accepted'
            ).first()

            if not friendship:
                return Response(
                    {"message": "Friendship not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            friendship.delete()
            
            # Log successful removal
            logger.info(f"Friendship removed between {user_profile.id} and {friend_profile.id}")
            
            return Response(
                {"message": "Friend removed successfully"}, 
                status=status.HTTP_200_OK
            )
            
        except Profile.DoesNotExist:
            logger.error(f"Profile not found: {friend_profile_id}")
            return Response(
                {"message": "Profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error removing friend: {str(e)}")
            return Response(
                {"message": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateOnlineStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
            status = request.data.get('status', False)
            
            profile.is_online = status
            profile.save(update_fields=['is_online'])
            
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )