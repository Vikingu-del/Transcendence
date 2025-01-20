import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Profile, ChatModel, ChatNotification
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

            # Set user as online
            await self.set_user_online()

            # Notify friends about online status
            await self.notify_friends('online')

    async def disconnect(self, close_code):
        # Set user as offline
        await self.set_user_offline()

        # Notify friends about offline status
        await self.notify_friends('offline')

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def set_user_online(self):
        # Update the is_online field without loading the entire profile
        Profile.objects.filter(user_id=self.user.id).update(is_online=True)

    @database_sync_to_async
    def set_user_offline(self):
        # Update the is_online field without loading the entire profile
        Profile.objects.filter(user_id=self.user.id).update(is_online=False)

    async def notify_friends(self, status):
        # Get friend user IDs asynchronously
        friend_user_ids = await self.get_friend_user_ids()

        message = {
            'type': 'friend_status',
            'user_id': self.user.id,
            'status': status,
        }

        for user_id in friend_user_ids:
            group_name = f"user_{user_id}"
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'send_notification',
                    'message': message,
                }
            )

    @database_sync_to_async
    def get_friend_user_ids(self):
        # Obtain friend profiles and extract user IDs
        friends = self.user.profile.get_friends()
        return [friend.user_id for friend in friends]

    async def send_friend_request_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_request',
            'from_user_id': event['from_user_id'],
            'from_user_name': event['from_user_name'],
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        query_string = self.scope['query_string'].decode()
        query_params = dict(qc.split('=') for qc in query_string.split('&'))
        other_user_id = query_params.get('friend_id')
        
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

        # Save the message to the database
        await self.save_message(username, self.room_group_name, message, receiver)

        # Send the message to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        # Save message to the database
        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        
        # Ensure other_user_id is available
        other_user_id = self.scope['query_string'].decode().split('=')[1]
        get_user = User.objects.get(id=other_user_id)
        
        # Handle notification creation if the receiver is the user we're sending to
        if receiver == get_user.username:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)