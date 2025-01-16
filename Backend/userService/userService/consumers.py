import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Profile, ChatModel, ChatNotification # Import necessary models
from django.contrib.auth.models import User  # Import User model

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

            # Add the user to the "online_users" group
            await self.channel_layer.group_add("online_users", self.channel_name)

            # Send the list of online users to the newly connected user
            await self.send_online_users_list()

            # Notify other users of this user's login
            await self.channel_layer.group_send(
                "online_users",
                {
                    "type": "user_login",
                    "username": self.user.username,
                },
            )

    async def disconnect(self, close_code):
        # Set user as offline
        await self.set_user_offline()

        # Notify friends about offline status
        await self.notify_friends('offline')

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        if self.user.is_authenticated:
            # Remove the user from the "online_users" group
            await self.channel_layer.group_discard("online_users", self.channel_name)

            # Notify other users of this user's logout
            await self.channel_layer.group_send(
                "online_users",
                {
                    "type": "user_logout",
                    "username": self.user.username,
                },
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'message' in data:
            message = data['message']
            username = data['username']
            receiver = data['receiver']

            await self.save_message(username, self.group_name, message, receiver)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )
        else:
            pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

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

    async def send_online_users_list(self):
        # Retrieve the online users and send to the connected client
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({"type": "online_users_list", "users": online_users}))

    @database_sync_to_async
    def get_online_users(self):
        # Query all currently authenticated users
        current_username = self.scope["user"].username
        user_list = Profile.objects.filter(is_online=True).exclude(user__username=current_username)

        return [x.user.username for x in user_list]

    async def user_login(self, event):
        await self.send(text_data=json.dumps({"type": "user_login", "username": event["username"]}))

    async def user_logout(self, event):
        await self.send(text_data=json.dumps({"type": "user_logout", "username": event["username"]}))

    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        other_user_id = self.scope['url_route']['kwargs']['id']
        get_user = User.objects.get(id=other_user_id)
        if receiver == get_user.username:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)