from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Chat
from .serializers import ChatSerializer, ChatListSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
import requests
from django.conf import settings
from rest_framework.exceptions import NotFound

logger = logging.getLogger(__name__)

class ChatListView(generics.ListAPIView):
    serializer_class = ChatListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(participant1=user) | Chat.objects.filter(participant2=user)
    

class ChatDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_object(self):
        # logger.debug(f"Request headers: {self.request.headers}")
        # logger.debug(f"Auth: {self.request.auth}")
        logger.debug(f"User: {self.request.user}")

        chat_id = self.kwargs['id']
        # First try to find existing chat
        chat = Chat.objects.filter(id=chat_id).first()
        
        if not chat:
            try:
                # Parse the user IDs from chat_id
                user1_id, user2_id = map(int, chat_id.split('_'))
                
                # Sort user IDs to ensure consistent chat ID creation
                sorted_user_ids = sorted([user1_id, user2_id])
                consistent_chat_id = f"{sorted_user_ids[0]}_{sorted_user_ids[1]}"
                
                # Check again with consistent chat ID
                chat = Chat.objects.filter(id=consistent_chat_id).first()
                
                if not chat:
                    auth_header = self.request.headers.get('Authorization')
                    user1_data = fetch_user_from_service(sorted_user_ids[0], auth_header)
                    user2_data = fetch_user_from_service(sorted_user_ids[1], auth_header)
                    
                    # Create or get User objects
                    user1 = User.objects.get_or_create(
                        id=user1_data['id'],
                        defaults={'username': user1_data['username']}
                    )[0]
                    
                    user2 = User.objects.get_or_create(
                        id=user2_data['id'],
                        defaults={'username': user2_data['username']}
                    )[0]
                    
                    # Create chat with consistent ID
                    chat = Chat.objects.create(
                        id=consistent_chat_id,
                        participant1=user1,
                        participant2=user2
                    )
            except Exception as e:
                logger.error(f"Chat creation error: {str(e)}")
                raise
        
        return chat

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'id': serializer.data['id'],
            'participant1': serializer.data['participant1_info'],
            'participant2': serializer.data['participant2_info'],
            'messages': serializer.data['messages']
        })

def fetch_user_from_service(user_id, auth_header):
    """
    Fetch user information from the user service
    """
    try:
        url = f"{settings.USER_SERVICE_URL}/api/user/verify/"
        headers = {
            'Authorization': auth_header
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch user {user_id}. Status: {response.status_code}")
            raise NotFound(f"User with id {user_id} not found")
            
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise NotFound(f"User with id {user_id} not found")