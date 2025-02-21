import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from .models import Chat, Message
from django.utils import timezone
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get token and chat_id from query parameters
            query_string = parse_qs(self.scope['query_string'].decode())
            token_key = query_string.get('token', [None])[0]
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']

            if not token_key or not self.chat_id:
                await self.close(code=4001)
                return

            # Authenticate user
            self.user = await self.get_user_from_token(token_key)
            logger.debug(f"Authenticated user: {self.user}")
            if not self.user:
                await self.close(code=4002)
                return

            # Join chat group
            await self.channel_layer.group_add(
                f"chat_{self.chat_id}",
                self.channel_name
            )
            await self.accept()
            logger.debug(f"WebSocket connection accepted for chat {self.chat_id}")

        except Exception as e:
            logger.error(f'Chat connection error: {str(e)}')
            await self.close(code=4000)

    async def disconnect(self, close_code):
        if hasattr(self, 'chat_id'):
            await self.channel_layer.group_discard(
                f"chat_{self.chat_id}",
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] != 'chat_message':
                return

            if 'message' not in data or 'text' not in data['message']:
                logger.error('Invalid message format')
                return

            saved_message = await self.save_message(
                chat_id=self.chat_id,
                sender=self.user,
                text=data['message']['text']
            )

            # Format the message for broadcasting
            message_data = {
                'type': 'chat.message',
                'message': {
                    'id': str(saved_message.id),
                    'chat': self.chat_id,
                    'sender': self.user.id,
                    'text': saved_message.text,
                    'created_at': saved_message.created_at.isoformat()
                }
            }

            # Broadcast to the chat group
            await self.channel_layer.group_send(
                f"chat_{self.chat_id}",
                message_data
            )

        except Exception as e:
            logger.error(f'Error in chat receive: {str(e)}')


    async def chat_message(self, event):
        message = event['message']
        
        # Format message before sending
        formatted_message = {
            'id': str(message.get('id')),
            'chat': str(message.get('chat')),
            'sender': str(message.get('sender')),
            'text': message.get('text'),
            'created_at': message.get('created_at')
        }
        
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': formatted_message
        }))

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            # Remove the profile from select_related since it's causing the error
            token = Token.objects.select_related('user').get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, chat_id, sender, text):
        try:
            chat = Chat.objects.get(id=chat_id)
            message = Message.objects.create(
                chat=chat,
                sender=sender,
                text=text
            )
            # Force refresh to get the created_at timestamp
            message.refresh_from_db()
            return message
        except Chat.DoesNotExist:
            # Create chat if doesn't exist
            user_ids = chat_id.split('_')
            if len(user_ids) != 2:
                raise ValueError("Invalid chat_id format")
                
            chat = Chat.objects.create(
                participant1_id=user_ids[0],
                participant2_id=user_ids[1]
            )
            message = Message.objects.create(
                chat=chat,
                sender=sender,
                text=text
            )
            message.refresh_from_db()
            return message