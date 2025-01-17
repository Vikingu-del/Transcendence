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
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'{self.room_name}'

        logger.debug(f"Connecting to room: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from room: {self.room_group_name}")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']

        logger.debug(f"Received message: {message} from sender: {sender.username}")

        # Save message to the database
        await self.save_message(sender, self.room_group_name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'sender_display_name': sender.get_full_name(),  # Include sender's display name
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        sender_display_name = event['sender_display_name']  # Get sender's display name

        logger.debug(f"Sending message: {message} from sender: {sender} ({sender_display_name})")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'sender_display_name': sender_display_name,  # Include sender's display name
        }))
        
    @database_sync_to_async
    def save_message(self, sender, thread_name, message):
        logger.debug(f"Saving message to thread: {thread_name}")

        # Validate and parse thread_name
        try:
            parts = thread_name.split('_')
            if len(parts) != 3:
                raise ValueError("Invalid thread_name format. Expected format: 'thread_user1ID_user2ID'")
            
            _, user1_id, user2_id = parts
            user1_id = int(user1_id)
            user2_id = int(user2_id)
        except ValueError as e:
            logger.error(f"Error parsing thread_name '{thread_name}': {e}")
            return

        # Determine the receiver
        try:
            receiver_id = user2_id if sender.id == user1_id else user1_id
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            logger.error(f"Receiver with ID {receiver_id} does not exist.")
            return

        # Save the message
        try:
            ChatModel.objects.create(sender=sender, receiver=receiver, thread_name=thread_name, message=message)
            logger.debug(f"Message saved successfully in thread: {thread_name}")
        except Exception as e:
            logger.error(f"Error saving message to database: {e}")
