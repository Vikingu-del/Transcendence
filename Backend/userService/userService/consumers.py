import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from .models import Profile, Chat, Message
from django.utils import timezone
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Authentication
            query_string = parse_qs(self.scope['query_string'].decode())
            token_key = query_string.get('token', [None])[0]
            chat_id = query_string.get('chat_id', [None])[0]

            if not token_key:
                await self.close(code=4001)
                return

            # Get user and validate
            self.user = await self.get_user_from_token(token_key)
            if not self.user or not hasattr(self.user, 'profile'):
                await self.close(code=4002)
                return

            # Set up user's notification group
            self.notification_group = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.notification_group, self.channel_name)

            # Set up chat group if chat_id provided
            if chat_id:
                self.chat_group = f"chat_{chat_id}"
                await self.channel_layer.group_add(self.chat_group, self.channel_name)

            # Accept connection and set online
            await self.accept()
            await self.set_user_online()
            await self.notify_friends('online')

        except Exception as e:
            logger.error(f'Connection error: {str(e)}')
            await self.close(code=4000)

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user and hasattr(self.user, 'profile'):
            try:
                await self.set_user_offline()
                await self.notify_friends('offline')
                
                # Proper group cleanup
                if hasattr(self, 'notification_group'):
                    await self.channel_layer.group_discard(
                        self.notification_group, 
                        self.channel_name
                    )
                if hasattr(self, 'chat_group'):
                    await self.channel_layer.group_discard(
                        self.chat_group, 
                        self.channel_name
                    )

                logger.info(f'User {self.user.id} disconnected from WebSocket')
            except Exception as e:
                logger.error(f'Error in disconnect: {str(e)}')

    async def chat_message(self, event):
        """Handle chat message broadcast"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f'Error sending chat message: {str(e)}')

    async def handle_friend_status(self, data):
        """Handle friend status updates"""
        try:
            status = data.get('status')
            if status in ['online', 'offline']:
                await self.notify_friends(status)
        except Exception as e:
            logger.error(f'Error handling friend status: {str(e)}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            handlers = {
                'friend_request': self.handle_friend_request,
                'chat_message': self.handle_chat_message,
                'friend_status': self.handle_friend_status,
                'friend_removed': self.handle_friend_removed
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                logger.warning(f'Unknown message type: {message_type}')

        except Exception as e:
            logger.error(f'Receive error: {str(e)}')

    async def handle_chat_message(self, data):
        try:
            chat_id = data.get('chat_id')
            message = data.get('message')
            
            if not chat_id or not message:
                return

            # Save to database
            saved_message = await self.save_chat_message(
                chat_id=chat_id,
                sender=self.user,
                text=message
            )

            # Broadcast to chat group
            await self.channel_layer.group_send(
                f"chat_{chat_id}",
                {
                    'type': 'chat.message',
                    'message': {
                        'id': saved_message.id,
                        'sender_id': self.user.id,
                        'sender_name': self.user.username,
                        'text': message,
                        'timestamp': str(saved_message.created_at)
                    }
                }
            )

        except Exception as e:
            logger.error(f'Chat message error: {str(e)}')

    async def handle_friend_request(self, data):
        """Handle incoming friend request notifications"""
        try:
            # Extract data
            to_user_id = data.get('to_user_id')
            from_user_id = self.user.id
            
            # Get user profiles
            to_user = await self.get_user_profile(to_user_id)
            from_user = await self.get_user_profile(from_user_id)
            
            if not to_user or not from_user:
                logger.error(f'User profile not found for friend request')
                return

            # Send notification to recipient's group channel
            await self.channel_layer.group_send(
                f'user_{to_user_id}',
                {
                    'type': 'friend_request_notification',
                    'from_user_id': from_user_id,
                    'from_user_name': from_user.user.username,
                    'from_user_avatar': from_user.avatar.url if from_user.avatar else None
                }
            )
            
            logger.info(f'Friend request sent from user {from_user_id} to user {to_user_id}')

        except Exception as e:
            logger.error(f'Error handling friend request: {str(e)}')

    async def friend_request_notification(self, event):
        """Send friend request notification to WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'friend_request',
                'from_user_id': event['from_user_id'],
                'from_user_name': event['from_user_name'],
                'from_user_avatar': event['from_user_avatar']
            }))
        except Exception as e:
            logger.error(f'Error sending friend request notification: {str(e)}')

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            return Token.objects.select_related('user', 'user__profile').get(key=token_key).user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def set_user_online(self):
        try:
            self.user.profile.is_online = True
            self.user.profile.save(update_fields=['is_online'])
        except Exception as e:
            logger.error(f'Error setting user online: {str(e)}')
            raise

    @database_sync_to_async
    def set_user_offline(self):
        try:
            self.user.profile.is_online = False
            self.user.profile.save(update_fields=['is_online'])
        except Exception as e:
            logger.error(f'Error setting user offline: {str(e)}')
            raise

    @database_sync_to_async
    def get_friend_user_ids(self):
        try:
            return [friend.user.id for friend in self.user.profile.get_friends()]
        except Exception as e:
            logger.error(f'Error getting friend IDs: {str(e)}')
            return []
    
    @database_sync_to_async
    def save_chat_message(self, chat_id, sender, text):
        chat = Chat.objects.get(id=chat_id)
        return Message.objects.create(
            chat=chat,
            sender=sender,
            text=text
        )


    async def notify_friends(self, status):
        try:
            friend_user_ids = await self.get_friend_user_ids()
            if not friend_user_ids:
                return

            message = {
                'type': 'friend_status',
                'user_id': self.user.id,
                'user_name': self.user.profile.display_name,
                'status': status,
                'timestamp': str(timezone.now())
            }
            
            for user_id in friend_user_ids:
                await self.channel_layer.group_send(
                    f"user_{user_id}",
                    {
                        'type': 'send_notification',
                        'message': message
                    }
                )
        except Exception as e:
            logger.error(f'Error in notify_friends: {str(e)}')

    async def send_notification(self, event):
        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            logger.error(f'Error in send_notification: {str(e)}')
