import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import ChatModel, UserProfileModel, ChatNotification
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async


class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        other_user_id = self.scope['url_route']['kwargs'].get('id')
        
        if int(my_id) < int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        receiver = data['receiver']

        await self.save_message(username, self.room_group_name, message, receiver)

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

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        other_user_id = self.scope['url_route']['kwargs']['id']
        get_user = User.objects.get(id=other_user_id)
        if receiver == get_user.username:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)


class OnlineUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Accept the WebSocket connection first
            await self.accept()
            
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
        else:
            # Reject the WebSocket connection if the user is not authenticated
            await self.close()


    async def disconnect(self, close_code):
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

    async def send_online_users_list(self):
        # Retrieve the online users and send to the connected client
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({"type": "online_users_list", "users": online_users}))

    @sync_to_async
    def get_online_users(self):
        # Query all currently authenticated users
        current_username = self.scope["user"].username
        user_list = UserProfileModel.objects.filter(online_status=True).exclude(user__username=current_username)

        return ([x.user.username for x in user_list])

    async def user_login(self, event):
        await self.send(text_data=json.dumps({"type": "user_login", "username": event["username"]}))

    async def user_logout(self, event):
        await self.send(text_data=json.dumps({"type": "user_logout", "username": event["username"]}))
