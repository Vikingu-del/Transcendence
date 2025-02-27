import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from pong.models import GameSession
from asgiref.sync import async_to_sync

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope['user']
            self.user_group_name = f"user_{self.user.id}"
            self.notifications_group = "game_notifications"

            if not self.user or self.user.is_anonymous:
                print("User not authenticated")
                await self.close(code=4003)
                return

            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.channel_layer.group_add(
                self.notifications_group,
                self.channel_name
            )
            
            await self.accept()

        except Exception as e:
            print(f"Error in notification connect: {str(e)}")
            await self.close(code=4000)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'game_invite':
                await self.handle_game_invite(data)
            elif message_type == 'game_accepted':
                await self.handle_game_accept(data)
            elif message_type == 'game_declined':
                await self.handle_game_decline(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'friend_request':
                await self.handle_friend_request(data)
            elif message_type == 'friend_accepted':
                await self.handle_friend_accept(data)
            elif message_type == 'friend_declined':
                await self.handle_friend_decline(data)
            elif message_type == 'friend_removed':
                await self.handle_friend_removed(data)

        except Exception as e:
            print(f"Error processing notification: {str(e)}")

    async def disconnect(self, close_code):
        try:
            # Leave both groups
            if hasattr(self, 'user_group_name'):
                await self.channel_layer.group_discard(
                    self.user_group_name,
                    self.channel_name
                )
            if hasattr(self, 'notifications_group'):
                await self.channel_layer.group_discard(
                    self.notifications_group,
                    self.channel_name
                )
        except Exception as e:
            print(f"Error in notification disconnect: {str(e)}")
    
    async def handle_game_invite(self, data):
        """Handle game invites"""
        try:
            recipient_id = data.get('recipient_id')
            message = {
                'type': 'game_invite',
                'game_id': data['game_id'],
                'sender_id': self.user.id,
                'sender_name': data['sender_name'],
                'recipient_id': recipient_id
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=self.user.id,
                notification_type='game_invite',
                content=message
            )
            
            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'game.invite',
                    'message': message
                }
            )
        except Exception as e:
            print(f"Error handling game invite: {str(e)}")

    async def game_invite(self, event):
        """Forward game invite to client"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            print(f"Error sending game invite: {str(e)}")

    async def handle_game_accept(self, data):
        """Handle game acceptance"""
        try:
            message = {
                'type': 'game_state',
                'game_status': 'accepted',
                'sender_id': data['sender_id'],
                'recipient_id': data['recipient_id'],
                'sender_name': data['sender_name'],
                'recipient_name': data['recipient_name']
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=data['recipient_id'],
                sender_id=data['sender_id'],
                notification_type='game_accepted',
                content=message
            )
            
            await self.channel_layer.group_send(
                f"pong_{data['game_id']}", 
                {
                    'type': 'game_state_update',
                    'message': message
                }
            )
        except Exception as e:
            print(f"Error handling game accept: {str(e)}")

    async def handle_game_decline(self, data):
        """Handle game decline from client"""
        try:
            sender_id = data.get('sender_id')
            
            # Save notification to database
            await self.save_notification(
                recipient_id=sender_id,
                sender_id=self.user.id,
                notification_type='game_declined',
                content=data
            )
            
            await self.channel_layer.group_send(
                f"user_{sender_id}",
                {
                    'type': 'game.decline',
                    'message': data
                }
            )
        except Exception as e:
            print(f"Error handling game decline: {str(e)}")

    async def handle_chat_message(self, data):
        """Handle chat message notifications"""
        try:
            message = data.get('message', {})
            recipient_id = message.get('recipient_id')
            
            if not recipient_id:
                print('No recipient_id provided in chat notification')
                return

            # Format notification message
            notification_data = {
                'type': 'chat_message',
                'sender_id': str(message.get('sender_id')),  # Convert to string
                'sender_name': message.get('sender_name', 'Unknown User'),
                'recipient_id': str(recipient_id),  # Convert to string
                'text': message.get('text', '')
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=self.user.id,
                notification_type='chat_message',
                content=notification_data
            )

            # Send to recipient's group
            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'chat.notification',
                    'message': notification_data
                }
            )            
        except Exception as e:
            print(f"Error handling chat notification: {str(e)}")

    async def handle_friend_request(self, data):
        """Handle friend request notifications"""
        try:
            recipient_id = data.get('recipient_id')
            sender_id = data.get('sender_id')  # Get the sender_id from the data
        
            # Don't send friend requests to yourself
            if int(recipient_id) == int(sender_id): 
                print(f"Preventing self-request from user {sender_id}")
                return
            
            # Check if sender_name is in the top-level data
            sender_name = data.get('sender_name', self.user.username)
            
            message = {
                'type': 'friend_request',
                'sender_id': sender_id,
                'sender_name': sender_name,
                'recipient_id': recipient_id
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type='friend_request',
                content=message
            )

            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'friend.request',
                    'message': message
                }
            )
            print(f"Friend request sent to user_{recipient_id}, sender: {sender_name}")
        except Exception as e:
            print(f"Error handling friend request: {str(e)}")

    async def handle_friend_accept(self, data):
        """Handle friend acceptance notifications"""
        try:
            recipient_id = data.get('recipient_id')
            sender_id = data.get('sender_id')

            # Don't send accept notifications to yourself
            if int(recipient_id) == int(sender_id): 
                print(f"Preventing self-notification from user {sender_id}")
                return
            
            # Get sender name
            sender_name = data.get('sender_name', self.user.username)
            
            message = {
                'type': 'friend_accepted',
                'sender_id': sender_id,
                'sender_name': sender_name,
                'recipient_id': recipient_id
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type='friend_accepted',
                content=message
            )

            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'friend.accepted',
                    'message': message
                }
            )
            print(f"Friend accept sent to user_{recipient_id}, acceptor: {sender_name}")
        except Exception as e:
            print(f"Error handling friend accept: {str(e)}")

    async def handle_friend_decline(self, data):
        """Handle friend decline notifications"""
        try:
            recipient_id = data.get('recipient_id')
            sender_id = data.get('sender_id')

            # Don't send decline notifications to yourself
            if int(recipient_id) == int(sender_id): 
                print(f"Preventing self-notification from user {sender_id}")
                return
            
            # Get sender name
            sender_name = data.get('sender_name', self.user.username)
            
            message = {
                'type': 'friend_declined',
                'sender_id': sender_id,
                'sender_name': sender_name,
                'recipient_id': recipient_id
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type='friend_declined',
                content=message
            )

            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'friend.declined',
                    'message': message
                }
            )
            print(f"Friend decline sent to user_{recipient_id}, decliner: {sender_name}")
        except Exception as e:
            print(f"Error handling friend decline: {str(e)}")

    async def handle_friend_removed(self, data):
        """Handle friend removal notifications"""
        try:
            recipient_id = data.get('recipient_id')
            sender_id = data.get('sender_id')

            # Don't send removal notifications to yourself
            if int(recipient_id) == int(sender_id): 
                print(f"Preventing self-notification from user {sender_id}")
                return
            
            # Get sender name
            sender_name = data.get('sender_name', self.user.username)
            
            message = {
                'type': 'friend_removed',
                'sender_id': sender_id,
                'sender_name': sender_name,
                'recipient_id': recipient_id
            }
            
            # Save notification to database
            await self.save_notification(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type='friend_removed',
                content=message
            )

            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'friend.removed',
                    'message': message
                }
            )
            print(f"Friend removal sent to user_{recipient_id}, remover: {sender_name}")
        except Exception as e:
            print(f"Error handling friend removal: {str(e)}")

    async def friend_removed(self, event):
        """Forward friend removal to client"""
        try:
            print(f"Forwarding friend removal: {event}")
            await self.send(text_data=json.dumps(event['message']))
            print(f"Friend removal forwarded successfully")
        except Exception as e:
            print(f"Error sending friend removal: {str(e)}")

    async def friend_declined(self, event):
        """Forward friend decline to client"""
        try:
            print(f"Forwarding friend decline: {event}")
            await self.send(text_data=json.dumps(event['message']))
            print(f"Friend decline forwarded successfully")
        except Exception as e:
            print(f"Error sending friend decline: {str(e)}")

    async def friend_accepted(self, event):
        """Forward friend acceptance to client"""
        try:
            print(f"Forwarding friend acceptance: {event}")
            await self.send(text_data=json.dumps(event['message']))
            print(f"Friend acceptance forwarded successfully")
        except Exception as e:
            print(f"Error sending friend acceptance: {str(e)}")

    async def friend_request(self, event):
        """Forward friend request to client"""
        try:
            print(f"Forwarding friend request: {event}")
            await self.send(text_data=json.dumps(event['message']))
            print(f"Friend request forwarded successfully")
        except Exception as e:
            print(f"Error sending friend request: {str(e)}")

    async def chat_notification(self, event):
        """Send chat notification to client"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            print(f"Error sending chat notification: {str(e)}")

    async def game_accept(self, event):
        """Handle game accept from channel layer"""
        try:
            message = event['message']
            await self.channel_layer.group_send(
                f"pong_{message['game_id']}", 
                {
                    'type': 'game_state_update',
                    'message': {
                        'type': 'game_state',
                        'game_id': message['game_id'],
                        'player1_username': message['player1_name'],
                        'player2_username': message['player2_name'],
                        'game_status': 'accepted'
                    }
                }
            )
            
            # Also send the direct acceptance message
            await self.send(text_data=json.dumps({
                'type': 'game_accepted',
                'game_id': message['game_id'],
                'sender_id': message['sender_id'],
                'recipient_id': message['recipient_id'],
                'sender_name': message['sender_name'],
                'recipient_name': message['recipient_name'],
                'player1_name': message['player1_name'],
                'player2_name': message['player2_name']
            }))
        except Exception as e:
            print(f"Error sending game accept: {str(e)}")

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def game_decline(self, event):
        """Handle game decline from channel layer"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            print(f"Error sending game decline: {str(e)}")

    @database_sync_to_async
    def save_notification(self, recipient_id, sender_id, notification_type, content):
        """Save notification to database"""
        try:
            recipient = User.objects.get(id=recipient_id)
            sender = User.objects.get(id=sender_id)
            
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                content=content
            )
            return True
        except Exception as e:
            print(f"Error saving notification: {str(e)}")
            return False
