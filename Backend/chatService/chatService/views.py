from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Chat
from .serializers import ChatSerializer, ChatListSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ChatListView(generics.ListAPIView):
    serializer_class = ChatListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(participant1=user) | Chat.objects.filter(participant2=user)
    
import logging

logger = logging.getLogger(__name__)

class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Debug authentication
        logger.debug(f"Request headers: {self.request.headers}")
        logger.debug(f"Auth: {self.request.auth}")
        logger.debug(f"User: {self.request.user}")

        chat_id = self.kwargs['id']
        chat = Chat.objects.filter(id=chat_id).first()
        
        if not chat:
            try:
                user1_id, user2_id = map(int, chat_id.split('_'))
                user1 = get_object_or_404(User, id=user1_id)
                user2 = get_object_or_404(User, id=user2_id)
                
                chat = Chat.objects.create(
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