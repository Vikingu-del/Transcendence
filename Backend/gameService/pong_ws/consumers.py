import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

import logging
logger = logging.getLogger(__name__)
from pong.models import GameSession
from asgiref.sync import async_to_sync

@database_sync_to_async
def save_game_session(game_session):
    """ Safely save the game session asynchronously. """
    game_session.save()

@database_sync_to_async
def save_final_score(game_id, winner_username, player1_score, player2_score):
    """ Save final scores when the game ends. """
    game_session = GameSession.objects.filter(game_id=game_id).order_by('-created_at').first()
    if not game_session:
        return

    winner = User.objects.get(username=winner_username)
    game_session.winner = winner
    game_session.player1_score = player1_score
    game_session.player2_score = player2_score
    game_session.ended_at = timezone.now()
    game_session.is_active = False
    game_session.save()


@database_sync_to_async
def reset_game_session(game_id):
    """ Reset the game session for a new game. """
    game_session = GameSession.objects.get(game_id=game_id)
    game_session.player1_score = 0
    game_session.player2_score = 0
    game_session.player1_paddle = 0
    game_session.player2_paddle = 0
    game_session.ball_position = {}
    game_session.ball_direction = {}
    game_session.is_active = True
    game_session.ended_at = None
    game_session.save()
    return game_session.game_id

@database_sync_to_async
def create_game_session(game_id, player1=None, player2=None):
<<<<<<< HEAD
    """Create a new game session with given game_id and optional players."""
    try:
        game_uuid = uuid.UUID(game_id)
=======
    """Create a new game session with improved error handling and validation"""
    try:
        # Validate game_id format
        try:
            game_uuid = uuid.UUID(game_id)
        except ValueError:
            logger.error(f"Invalid game ID format: {game_id}")
            return None

        # Mark any existing active sessions for this game as inactive
        GameSession.objects.filter(game_id=game_uuid).update(is_active=False)

        # Create new session
>>>>>>> refs/remotes/origin/final_structure_copy
        game_session = GameSession.objects.create(
            game_id=game_uuid,
            player1=player1,
            player2=player2,
            is_active=True,
            ball_position={"x": 400, "y": 200},
            ball_direction={"dx": 3, "dy": 3}
        )
<<<<<<< HEAD
        print(f"Created new game session: {game_session.game_id}")
        return game_session
    except Exception as e:
        print(f"Error creating game session: {str(e)}")
        return None

=======

        logger.info(f"Created game session: {game_session.game_id} with players: "
                   f"{player1.username if player1 else 'None'} vs "
                   f"{player2.username if player2 else 'None'}")
        return game_session

    except Exception as e:
        logger.error(f"Error creating game session: {str(e)}")
        return None
>>>>>>> refs/remotes/origin/final_structure_copy

@database_sync_to_async
def create_rematch_session(game_id, player1, player2):
    """Create a new game session for a rematch, keeping the same players."""
    try:
        # Mark old games with this ID as inactive
        GameSession.objects.filter(game_id=game_id).update(is_active=False)
        
        # Create new session with same game_id
        return create_game_session(game_id, player1, player2)
    except Exception as e:
        print(f"Error creating rematch session: {str(e)}")
        return None


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"pong_{self.game_id}"
        self.user = self.scope['user']
<<<<<<< HEAD
        self.user_group_name = f"user_{self.user.id}"
=======
>>>>>>> refs/remotes/origin/final_structure_copy

        if not self.user or self.user.is_anonymous:
            logger.error("User not authenticated")
            await self.close()
            return

        try:
<<<<<<< HEAD
            # Join game room group
=======
>>>>>>> refs/remotes/origin/final_structure_copy
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

<<<<<<< HEAD
            logger.info(f"Client connected and added to group {self.room_group_name}")

            # Initialize or get game session
            game_session = await self.get_game_session()
            if not game_session:
                game_session = await create_game_session(self.game_id, self.user)
                logger.info(f"Created new game session with ID: {self.game_id}")

            # Assign player roles and update game session
            game_session = await self.assign_players(game_session)
            
            # Get player names
            player1_username = await self.get_username(game_session.player1)
            player2_username = await self.get_username(game_session.player2) if game_session.player2 else "Waiting for Player 2"

            # Determine player role
            player_role = "spectator"
            if game_session.player1 == self.user:
                player_role = "player1"
            elif game_session.player2 == self.user:
                player_role = "player2"

            logger.info(f"Assigned Players: P1 -> {player1_username}, P2 -> {player2_username}")

            # Send initial game state to the connecting client
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'player1_username': player1_username,
                'player2_username': player2_username,
                'player_role': player_role
            }))

            # Broadcast updated player names to all clients in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_players',
                    'player1_username': player1_username,
                    'player2_username': player2_username
                }
            )

        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()
            return

    async def disconnect(self, close_code):
        game_session = await self.get_game_session()
        if game_session:
            winner = await sync_to_async(lambda: game_session.player1 if game_session.player1_score > game_session.player2_score else game_session.player2)()
            await save_final_score(self.game_id, winner.username, game_session.player1_score, game_session.player2_score)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'game_invite':
                recipient_id = data.get('recipient_id')
                recipient_group = f"user_{recipient_id}"
                
                logger.info(f"Sending game invite from {self.user.username} to group {recipient_group}")
                
                # Send to recipient's personal channel
                await self.channel_layer.group_send(
                    recipient_group,
                    {
                        'type': 'game_invite',
                        'sender_name': self.user.username,
                        'game_id': data['game_id'],
                        'sender_id': self.user.id
                    }
                )
        
            elif data.get('type') == 'game_invite_accept':
                # Handle game invite acceptance
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_start',
                        'game_id': data['game_id']
                    }
                )
            
            elif data.get('type') == 'game_invite_decline':
                # Handle game invite decline
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_declined',
                        'game_id': data['game_id']
                    }
                )
            # 🏆 Handle Game Over
            elif data.get('type') == 'game_over':
                await save_final_score(self.game_id, data['winner'], data['player1_score'], data['player2_score'])
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over_message',
                        'winner': data['winner'],
                        'player1_score': data['player1_score'],
                        'player2_score': data['player2_score']
                    }
                )
                return  # Exit early, no need to process further

            # 🎮 Handle New Game Request
            elif data.get('type') == 'new_game':
                game_session = await self.get_game_session()
                if game_session:
                    new_session = await create_rematch_session(
                        self.game_id,
                        game_session.player1,
                        game_session.player2
                    )
                    if new_session:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'new_game_id',
                                'new_game_id': str(new_session.game_id)
                            }
                        )

            # 🏓 Handle Paddle Movement
            if 'player1_paddle' in data or 'player2_paddle' in data:
                player1_paddle = data.get('player1_paddle', None)
                player2_paddle = data.get('player2_paddle', None)

                game_session = await self.get_game_session()
                game_session.player1_paddle = player1_paddle if player1_paddle is not None else game_session.player1_paddle
                game_session.player2_paddle = player2_paddle if player2_paddle is not None else game_session.player2_paddle
                await save_game_session(game_session)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_paddles',
                        'player1_paddle': game_session.player1_paddle,
                        'player2_paddle': game_session.player2_paddle
                    }
                )

            # 🏀 Handle Ball Movement (only Player 1 should broadcast)
            elif 'ballX' in data and 'ballY' in data:
                ballX = data['ballX']
                ballY = data['ballY']
                player1_score = data.get('player1_score', 0)
                player2_score = data.get('player2_score', 0)

                user = self.scope['user']
                game_session = await self.get_game_session()
                player1 = await database_sync_to_async(lambda: game_session.player1)()

                if player1 == user:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'update_ball',
                            'ballX': ballX,
                            'ballY': ballY,
                            'player1_score': player1_score,
                            'player2_score': player2_score
                        }
                    )
            
        except Exception as e:
            print(f"Error in receive: {str(e)}")


    # 🎮 Game Invite Handler   
    async def game_invite(self, event):
        logger.info(f"Delivering game invite to user from {event['sender_name']}")
        await self.send(text_data=json.dumps({
            'type': 'game_invite',
            'sender_name': event['sender_name'],
            'game_id': event['game_id'],
            'sender_id': event.get('sender_id')
        }))

    async def game_start(self, event):
        # Send game start to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_start',
            'game_id': event['game_id']
        }))

    async def game_declined(self, event):
        # Send game declined to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_declined',
            'game_id': event['game_id']
        }))

    # 🏆 Game Over Message Handler
    async def game_over_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
            'player1_score': event['player1_score'],
            'player2_score': event['player2_score']
        }))

=======
            # Initialize or get game session
            game_session = await self.get_game_session()
            if not game_session:
                game_session = await create_game_session(self.game_id, self.user)
                logger.info(f"Created new game session with ID: {self.game_id}")

            # Send initial game state
            await self.send_game_state(game_session)

        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            logger.info(f"Received game message type: {data.get('type')} from user {self.user.username}")
            
            # Handle only game-specific messages
            if data.get('type') == 'paddle_move':
                await self.handle_paddle_move(data)
            elif data.get('type') == 'ball_update':
                await self.handle_ball_update(data)
            elif data.get('type') == 'score_update':
                await self.handle_score_update(data)

        except Exception as e:
            logger.error(f"Error in game receive: {str(e)}")
            await self.send_error("Failed to process game message")

    async def disconnect(self, close_code):
        # Leave both groups
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def send_game_state(self, game_session):
        """Send current game state to client"""
        if not game_session:
            return

        game_session = await self.assign_players(game_session)
        player1_username = await self.get_username(game_session.player1)
        player2_username = await self.get_username(game_session.player2) if game_session.player2 else "Waiting for Player 2"

        # Determine player role
        player_role = "spectator"
        if game_session.player1 == self.user:
            player_role = "player1"
        elif game_session.player2 == self.user:
            player_role = "player2"

        logger.info(f"Sending game state: P1={player1_username}, P2={player2_username}, Role={player_role}")

        # Send game state to the client
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'player1_username': player1_username,
            'player2_username': player2_username,
            'player_role': player_role
        }))

>>>>>>> refs/remotes/origin/final_structure_copy
    # 🎮 New Game ID Handler
    async def new_game_id(self, event):
        await self.send(text_data=json.dumps({'type': 'new_game_id', 'new_game_id': event['new_game_id']}))


    async def update_paddles(self, event):
        # Send paddle data to clients
        await self.send(text_data=json.dumps({
            'player1_paddle': event['player1_paddle'],
            'player2_paddle': event['player2_paddle']
        }))


    async def update_players(self, event):
        print(f"Sending Player Update: {event['player1_username']} | {event['player2_username']}")  # Debugging
        await self.send(text_data=json.dumps({
            'player1_username': event['player1_username'],
            'player2_username': event['player2_username']
        }))

    async def update_ball(self, event):
        await self.send(text_data=json.dumps({
            'ballX': event['ballX'],
            'ballY': event['ballY'],
            'player1_score': event['player1_score'],
            'player2_score': event['player2_score']
        }))

    @database_sync_to_async
    def get_game_session(self):
        """Fetch the latest game session with the given game_id."""
        try:
            # Convert string to UUID if needed
            game_uuid = self.game_id if isinstance(self.game_id, uuid.UUID) else uuid.UUID(self.game_id)
            game_session = GameSession.objects.filter(game_id=game_uuid).order_by('-created_at').first()
            
            if game_session:
                print(f"Found game session with ID: {game_session.game_id}")
                return game_session
            else:
                print(f"No game session found with ID: {game_uuid}")
                return None
                
        except ValueError as e:
            print(f"Invalid UUID format: {self.game_id}")
            return None
        except Exception as e:
            print(f"Error getting game session: {str(e)}")
            return None
        
    async def initialize_game_session(self):
        """Initialize a new game session or get existing one."""
        try:
            # Get existing session
            game_session = await self.get_game_session()
            
            if not game_session:
                # Get the authenticated user
                user = self.scope['user']
                if not user or user.is_anonymous:
                    print("No authenticated user found")
                    return None

                print(f"Creating new game session with player1: {user.username}")
                
                # Create new session with the authenticated user as player1
                game_session = await create_game_session(
                    game_id=self.game_id,
                    player1=user  # Pass the authenticated user as player1
                )
                
                if game_session:
                    print(f"Successfully created game session with ID: {game_session.game_id}")
                else:
                    print("Failed to create game session")

            return game_session
        except Exception as e:
            print(f"Error initializing game session: {str(e)}")
            return None


    @database_sync_to_async
    def assign_players(self, game_session):
<<<<<<< HEAD
        """Assigns players correctly and prevents duplicate player assignment"""
        user = self.scope['user']
        logger.info(f"Connected User: {user.username}")

        if game_session.player1 is None:
            logger.info(f"Setting {user.username} as Player 1")
            game_session.player1 = user
        elif game_session.player2 is None and game_session.player1 != user:
            logger.info(f"Setting {user.username} as Player 2")
            game_session.player2 = user
            # Update the game session immediately when player2 joins
            game_session.save()
            # Broadcast the update to all clients
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_players',
                    'player1_username': game_session.player1.username,
                    'player2_username': user.username
                }
            )
        elif game_session.player1 == user:
            logger.info(f"{user.username} is already Player 1")
        elif game_session.player2 == user:
            logger.info(f"{user.username} is already Player 2")
        else:
            logger.info(f"Unexpected case: P1 -> {game_session.player1.username}, P2 -> {game_session.player2.username if game_session.player2 else 'None'}")

        game_session.save()
=======
        """Assigns players and updates their names"""
        user = self.scope['user']
        logger.info(f"Connected User: {user.username}")

        if not game_session.player1:
            game_session.player1 = user
            logger.info(f"Setting {user.username} as Player 1")
        elif not game_session.player2 and game_session.player1 != user:
            game_session.player2 = user
            logger.info(f"Setting {user.username} as Player 2")

        game_session.save()

        player1_name = game_session.player1.username if game_session.player1 else "Waiting"
        player2_name = game_session.player2.username if game_session.player2 else "Waiting for Player 2"

>>>>>>> refs/remotes/origin/final_structure_copy
        return game_session

    @database_sync_to_async
    def get_username(self, user):
<<<<<<< HEAD
        """Safely get the username of a user object asynchronously"""
        return user.username if user else "Waiting for Player 2"
=======
        """Get the display_name or username of a user"""
        if not user:
            return "Waiting for Player 2"
        # Try to get display_name first, fall back to username
        return getattr(user, 'display_name', user.username)
    
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope['user']
            self.user_group_name = f"user_{self.user.id}"
            self.notifications_group = "game_notifications"

            if not self.user or self.user.is_anonymous:
                logger.error("User not authenticated")
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
            logger.error(f"Error in notification connect: {str(e)}")
            await self.close(code=4000)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'game_invite':
                await self.handle_game_invite(data)
            elif message_type == 'game_accept':
                await self.handle_game_accept(data)
            elif message_type == 'game_decline':
                await self.handle_game_decline(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)

        except Exception as e:
            logger.error(f"Error processing notification: {str(e)}")

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
            logger.info(f"User {getattr(self, 'user', 'unknown')} disconnected from notifications")
        except Exception as e:
            logger.error(f"Error in notification disconnect: {str(e)}")
    
    async def handle_game_invite(self, data):
            """Handle game invites"""
            try:
                recipient_id = data.get('recipient_id')
                await self.channel_layer.group_send(
                    f"user_{recipient_id}",
                    {
                        'type': 'game.invite',
                        'message': {
                            'type': 'game_invite',
                            'game_id': data['game_id'],
                            'sender_id': self.user.id,
                            'sender_name': data['sender_name'],
                            'recipient_id': recipient_id
                        }
                    }
                )
                logger.info(f"Game invite sent to user_{recipient_id}")
            except Exception as e:
                logger.error(f"Error handling game invite: {str(e)}")

    async def game_invite(self, event):
        """Forward game invite to client"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending game invite: {str(e)}")

    async def handle_game_accept(self, data):
        """Handle game accept from client"""
        try:
            sender_id = data.get('sender_id')
            await self.channel_layer.group_send(
                f"user_{sender_id}",
                {
                    'type': 'game.accept',
                    'message': data
                }
            )
            logger.info(f"Game accept sent to user_{sender_id}")
        except Exception as e:
            logger.error(f"Error handling game accept: {str(e)}")

    async def handle_game_decline(self, data):
        """Handle game decline from client"""
        try:
            sender_id = data.get('sender_id')
            await self.channel_layer.group_send(
                f"user_{sender_id}",
                {
                    'type': 'game.decline',
                    'message': data
                }
            )
            logger.info(f"Game decline sent to user_{sender_id}")
        except Exception as e:
            logger.error(f"Error handling game decline: {str(e)}")

    async def handle_chat_message(self, data):
        """Handle chat message notifications"""
        try:
            message = data.get('message', {})
            recipient_id = message.get('recipient_id')
            
            if not recipient_id:
                logger.error('No recipient_id provided in chat notification')
                return

            # Format notification message
            notification_data = {
                'type': 'chat.notification',
                'message': {
                    'type': 'chat_message',
                    'sender_id': str(message.get('sender_id')),  # Convert to string
                    'sender_name': message.get('sender_name', 'Unknown User'),
                    'recipient_id': str(recipient_id),  # Convert to string
                    'text': message.get('text', '')
                }
            }

            # Send to recipient's group
            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                notification_data
            )
            
            logger.info(f"Chat notification sent to user_{recipient_id}")
            
        except Exception as e:
            logger.error(f"Error handling chat notification: {str(e)}")

    async def chat_notification(self, event):
        """Send chat notification to client"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending chat notification: {str(e)}")

    async def game_accept(self, event):
        """Handle game accept from channel layer"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending game accept: {str(e)}")

    async def game_decline(self, event):
        """Handle game decline from channel layer"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending game decline: {str(e)}")

            
>>>>>>> refs/remotes/origin/final_structure_copy
