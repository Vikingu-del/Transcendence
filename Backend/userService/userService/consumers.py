import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from .models import Profile
from django.utils import timezone
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            query_string = parse_qs(self.scope['query_string'].decode())
            token_key = query_string.get('token', [None])[0]

            if not token_key:
                await self.close(code=4001)
                return

            self.user = await self.get_user_from_jwt(token_key)
            if not self.user or not hasattr(self.user, 'profile'):
                await self.close(code=4002)
                return

            self.notification_group = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.notification_group, self.channel_name)
            
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
                
                if hasattr(self, 'notification_group'):
                    await self.channel_layer.group_discard(
                        self.notification_group, 
                        self.channel_name
                    )

            except Exception as e:
                logger.error(f'Error in disconnect: {str(e)}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            handlers = {
                'friend_request': self.handle_friend_request,
                'friend_status': self.handle_friend_status
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                logger.warning(f'Unknown message type: {message_type}')

        except Exception as e:
            logger.error(f'Receive error: {str(e)}', exc_info=True)

    async def handle_friend_request(self, data):
        """Handle incoming friend request notifications"""
        try:
            # Extract data
            to_user_id = data.get('to_user_id')
            from_user_id = self.user.id
            
            logger.info(f"Processing friend request from {from_user_id} to {to_user_id}")
            
            if not to_user_id:
                logger.error("No target user ID provided")
                return
                
            # Get user profiles
            to_user = await self.get_user_profile(to_user_id)
            from_user = await self.get_user_profile(from_user_id)
            
            if not to_user or not from_user:
                logger.error(f"Could not find profiles - to_user: {to_user}, from_user: {from_user}")
                return

            message = {
                'type': 'friend_request',
                'from_user_id': from_user_id,
                'from_user_name': from_user.display_name,
                'from_user_avatar': from_user.get_avatar_url()
            }
            
            logger.info(f"Sending notification to user_{to_user_id}: {message}")
            
            # Send notification to recipient's group channel
            await self.channel_layer.group_send(
                f"user_{to_user_id}",
                {
                    'type': 'send_notification',
                    'message': message
                }
            )

        except Exception as e:
            logger.error(f'Error in handle_friend_request: {str(e)}', exc_info=True)

        async def handle_friend_status(self, data):
            """Handle friend status change notifications"""
            try:
                # Extract status data
                status = data.get('status')
                if not status:
                    logger.error("No status provided in friend_status message")
                    return
                    
                # Notify friends of status change
                await self.notify_friends(status)
                
            except Exception as e:
                logger.error(f"Error handling friend status: {str(e)}", exc_info=True)

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
    def get_user_from_jwt(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return Token.objects.select_related('user', 'user__profile').get(id=user_id)
        except Exception as e:
            logger.error(f'JWT verification failed: {str(e)}')
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