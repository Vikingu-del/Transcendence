from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Chat
from .serializers import ChatSerializer, ChatListSerializer
from rest_framework.response import Response

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
        user2 = get_object_or_404(User, id=self.kwargs['id'])
        
        # Get or create chat
        chat = Chat.objects.filter(
            Q(participant1=user1, participant2=user2) | 
            Q(participant1=user2, participant2=user1)
        ).first()
        
        if not chat:
            chat = Chat.objects.create(
                participant1=user1,
                participant2=user2
            )
        
        # Prefetch related messages for better performance
        return Chat.objects.prefetch_related('messages').get(id=chat.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Restructure the response format
        return Response({
            'messages': serializer.data['messages']
        })