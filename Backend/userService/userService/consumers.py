import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from .models import Profile
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get token from query params
            query_string = parse_qs(self.scope['query_string'].decode())
            token_key = query_string.get('token', [None])[0]

            if not token_key:
                logger.warning('WebSocket connection attempt without token')
                await self.close(code=4001)
                return

            # Authenticate user with token
            self.user = await self.get_user_from_token(token_key)
            
            if not self.user or not hasattr(self.user, 'profile'):
                logger.warning(f'Invalid token or no profile: {token_key}')
                await self.close(code=4002)
                return

            # Initialize user's group and state
            self.group_name = f"user_{self.user.id}"
            self.heartbeat_received = True
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            
            # Accept connection and update status
            await self.accept()
            await self.set_user_online()
            await self.notify_friends('online')
            
            logger.info(f'User {self.user.id} connected to WebSocket')

        except Exception as e:
            logger.error(f'WebSocket connection error: {str(e)}')
            await self.close(code=4000)

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user and hasattr(self.user, 'profile'):
            try:
                await self.set_user_offline()
                await self.notify_friends('offline')
                if hasattr(self, 'group_name'):
                    await self.channel_layer.group_discard(self.group_name, self.channel_name)
                logger.info(f'User {self.user.id} disconnected from WebSocket')
            except Exception as e:
                logger.error(f'Error in disconnect: {str(e)}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            handlers = {
                'heartbeat': self.handle_heartbeat,
                'friend_request': self.handle_friend_request,
                'chat_message': self.handle_chat_message
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                logger.warning(f'Unknown message type: {message_type}')

        except json.JSONDecodeError:
            logger.error('Invalid JSON received')
        except Exception as e:
            logger.error(f'Error in receive: {str(e)}')

    async def handle_heartbeat(self, data):
        self.heartbeat_received = True
        await self.send(json.dumps({'type': 'heartbeat_response'}))

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
        if not self.heartbeat_received:
            logger.warning(f'Skipping notification for inactive user {self.user.id}')
            return

        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            logger.error(f'Error in send_notification: {str(e)}')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        query_string = self.scope['query_string'].decode()
        query_params = dict(qc.split('=') for qc in query_string.split('&'))
        other_user_id = query_params.get('friend_id')
        self.other_user_id = other_user_id
        
        if other_user_id is None:
            logger.error("other_user_id is None")
            await self.close()
            return

        if int(my_id) < int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'
        self.room_group_name = f'chat_{self.room_name}'

        logger.info(f'Connecting to room {self.room_group_name}')

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        else:
            logger.warning("room_group_name not set, skipping group discard.")

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        receiver = data['receiver']
        receiver_id = int(self.other_user_id)
        sender_id = int(self.scope['user'].id)  # Get sender's ID
        print(message)
        if sender_id < receiver_id:
            thread_name = f'chat_{sender_id}-{receiver_id}'
        else:
            thread_name = f'chat_{receiver_id}-{sender_id}'
    
        # Save the message to the database
        await self.save_message(username, thread_name, message, receiver)

        # Send the message to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'sender_id': sender_id,  # Include sender's ID
            }
        )

    async def chat_message(self, event):
        # Only send if current user is not the sender
        if self.scope['user'].id != event['sender_id']:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username']
            }))

    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        # Save message to the database
        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        
        # Ensure other_user_id is available
        other_user_id = self.scope['query_string'].decode().split('=')[1]
        get_user = User.objects.get(id=other_user_id)
        
        # # Handle notification creation if the receiver is the user we're sending to
        # if receiver == get_user.username:
        #     ChatNotification.objects.create(chat=chat_obj, user=get_user)