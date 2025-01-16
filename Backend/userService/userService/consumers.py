import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Profile, ChatModel, ChatNotification
from django.contrib.auth.models import User

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

    async def handle_chat_message(self, text_data_json):
        message = text_data_json['message']
        sender = self.scope['user'].username

        # Save message to the database
        await self.save_message(sender, self.room_group_name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))
