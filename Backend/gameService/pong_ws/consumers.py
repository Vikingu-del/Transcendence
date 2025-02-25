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
        game_session = GameSession.objects.create(
            game_id=game_uuid,
            player1=player1,
            player2=player2,
            is_active=True,
            ball_position={"x": 400, "y": 200},
            ball_direction={"dx": 3, "dy": 3}
        )

        logger.info(f"Created game session: {game_session.game_id} with players: "
                   f"{player1.username if player1 else 'None'} vs "
                   f"{player2.username if player2 else 'None'}")
        return game_session

    except Exception as e:
        logger.error(f"Error creating game session: {str(e)}")
        return None

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
        self.user_group_name = f"user_{self.scope['user'].id}"
        self.user = self.scope['user']

        if not self.user or self.user.is_anonymous:
            logger.error("User not authenticated")
            await self.close()
            return

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

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
            # logger.info(f"Received game message type: {data.get('type')} from user {self.user.username}")
            
            if data.get('type') == 'start_game':
                await self.handle_game_start(data)
            elif data.get('type') == 'paddle_move':
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

    async def handle_game_start(self, data):
        """Handle game start message"""
        try:
            game_session = await self.get_game_session()
            if not game_session:
                return

            # Broadcast game start to all players
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_state_update',
                        'message': {
                            'type': 'game_state',
                            'game_status': 'started',
                            'game_id': self.game_id,
                            'player1_username': await self.get_username(self.scope['user']),
                            'player2_username': await self.get_username(self.scope['user']),
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error handling game start: {str(e)}")

    async def handle_paddle_move(self, data):
        """Handle paddle movement updates from clients"""
        try:
            game_session = await self.get_game_session()
            if not game_session:
                logger.error("No game session found for paddle move")
                return

            # Determine which paddle to update based on player role
            player_role = await self.get_player_role(game_session)
            is_valid_player = player_role in ['player1', 'player2']

            if not is_valid_player:
                logger.warning(f"Invalid player trying to move paddle: {self.user.username}")
                return

            # Validate paddle position
            paddle_y = data.get('y', 0)
            if not isinstance(paddle_y, (int, float)):
                logger.warning(f"Invalid paddle position received: {paddle_y}")
                return

            # Update the paddle position in the game session
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_paddle_position',
                    'message': {
                        'type': 'paddle_move',
                        'player': player_role,
                        'y': paddle_y,
                        'player_id': self.user.id
                    }
                }
            )

            # logger.info(f"Paddle move processed for {player_role} at y={paddle_y}")

        except Exception as e:
            logger.error(f"Error handling paddle move: {str(e)}")
            await self.send_error("Failed to process paddle movement")

    async def update_paddle_position(self, event):
        """Send paddle position update to clients"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending paddle position update: {str(e)}")

    async def handle_ball_update(self, data):
        """Handle ball position and score updates"""
        try:
            game_session = await self.get_game_session()
            if not game_session:
                logger.error("No game session found for ball update")
                return

            # Only host (player1) should send ball updates
            player_role = await self.get_player_role(game_session)
            if player_role != 'player1':
                logger.warning(f"Non-host player trying to update ball: {self.user.username}")
                return

            # Validate ball data
            ball_data = data.get('ball', {})
            if not isinstance(ball_data, dict) or 'x' not in ball_data or 'y' not in ball_data:
                logger.warning(f"Invalid ball data received: {ball_data}")
                return

            score_data = data.get('score', {})
            if not isinstance(score_data, dict):
                logger.warning(f"Invalid score data received: {score_data}")
                return

            # Broadcast ball update to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_game_state',
                    'message': {
                        'type': 'ball_update',
                        'ball': ball_data,
                        'score': score_data
                    }
                }
            )

            # Update game session score if provided
            if 'player1' in score_data and 'player2' in score_data:
                game_session.player1_score = score_data['player1']
                game_session.player2_score = score_data['player2']
                await save_game_session(game_session)

            # logger.info(f"Ball update processed: pos=({ball_data.get('x')}, {ball_data.get('y')}), "
            #         f"score={score_data.get('player1', 0)}-{score_data.get('player2', 0)}")

        except Exception as e:
            logger.error(f"Error handling ball update: {str(e)}")
            await self.send_error("Failed to process ball update")

    async def update_game_state(self, event):
        """Send game state update to clients"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error sending game state update: {str(e)}")

    async def handle_score_update(self, data):
        """Handle score updates and check for game completion"""
        try:
            game_session = await self.get_game_session()
            if not game_session:
                logger.error("No game session found for score update")
                return

            # Only host (player1) should send score updates
            player_role = await self.get_player_role(game_session)
            if player_role != 'player1':
                logger.warning(f"Non-host player trying to update score: {self.user.username}")
                return

            # Validate score data
            score_data = data.get('score', {})
            if not isinstance(score_data, dict) or 'player1' not in score_data or 'player2' not in score_data:
                logger.warning(f"Invalid score data received: {score_data}")
                return

            # Update game session scores
            game_session.player1_score = score_data['player1']
            game_session.player2_score = score_data['player2']
            await save_game_session(game_session)

            # Check for game completion (e.g., if someone reached 11 points)
            winning_score = 11
            if score_data['player1'] >= winning_score or score_data['player2'] >= winning_score:
                # Determine winner
                winner_username = await self.get_username(game_session.player1 if score_data['player1'] > score_data['player2'] else game_session.player2)
                
                # Save final game state
                await save_final_score(
                    game_id=self.game_id,
                    winner_username=winner_username,
                    player1_score=score_data['player1'],
                    player2_score=score_data['player2']
                )

                # Broadcast game end to all players
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_game_state',
                        'message': {
                            'type': 'game_end',
                            'winner': winner_username,
                            'final_score': {
                                'player1': score_data['player1'],
                                'player2': score_data['player2']
                            }
                        }
                    }
                )
            else:
                # Broadcast regular score update
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_game_state',
                        'message': {
                            'type': 'score_update',
                            'score': score_data
                        }
                    }
                )

            logger.info(f"Score update processed: {score_data['player1']}-{score_data['player2']}")

        except Exception as e:
            logger.error(f"Error handling score update: {str(e)}")
            await self.send_error("Failed to process score update")

    async def send_game_state(self, game_session):
        """Send current game state to client"""
        if not game_session:
            return

        try:
            # Get player information asynchronously
            game_session = await self.assign_players(game_session)
            player1_username = await self.get_username(game_session.player1)
            player2_username = await self.get_username(game_session.player2) if game_session.player2 else "Waiting for Player 2"

            # Determine player role and host status
            is_host = game_session.player1 and game_session.player1.id == self.user.id
            player_role = await self.get_player_role(game_session)

            game_status = 'accepted' if game_session.player2 else 'waiting'
            
            logger.info(f"Sending game state: P1={player1_username}, P2={player2_username}, Role={player_role}, IsHost={is_host}")

            # Send the game state
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'game_status': game_status,
                'player1_username': player1_username,
                'player2_username': player2_username,
                'player_role': player_role,
                'is_host': is_host
            }))

        except Exception as e:
            logger.error(f"Error sending game state: {str(e)}")

    @database_sync_to_async
    def get_player_role(self, game_session):
        """Determine player role"""
        if game_session.player1 and game_session.player1.id == self.user.id:
            return "player1"
        elif game_session.player2 and game_session.player2.id == self.user.id:
            return "player2"
        return "spectator"

    async def game_state_update(self, event):
        """Handle game state updates"""
        try:
            message = event['message']
            game_session = await self.get_game_session()
            
            if game_session:
                # Update the message with current player role and host status
                message['player_role'] = await self.get_player_role(game_session)
                message['is_host'] = game_session.player1 and game_session.player1.id == self.user.id
            
            await self.send(text_data=json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error in game state update: {str(e)}")

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
                # print(f"Found game session with ID: {game_session.game_id}")
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
        """Assigns players and updates their names"""
        user = self.scope['user']
        logger.info(f"Connected User: {user.username}")

        try:
            # If user is already player1, keep that role
            if game_session.player1 and game_session.player1.id == user.id:
                logger.info(f"{user.username} is Player 1")
                return game_session

            # If user is already player2, keep that role
            if game_session.player2 and game_session.player2.id == user.id:
                logger.info(f"{user.username} is Player 2")
                return game_session

            # If player1 slot is empty, assign as player1
            if not game_session.player1:
                game_session.player1 = user
                logger.info(f"Setting {user.username} as Player 1")
            # If player2 slot is empty and user isn't player1, assign as player2
            elif not game_session.player2 and game_session.player1.id != user.id:
                game_session.player2 = user
                logger.info(f"Setting {user.username} as Player 2")

            game_session.save()
            return game_session
        except Exception as e:
            logger.error(f"Error assigning players: {str(e)}")
            return game_session

    # @database_sync_to_async
    # def assign_players(self, game_session):
    #     """Assigns players and updates their names"""
    #     user = self.scope['user']
    #     logger.info(f"Connected User: {user.username}")

    #     if not game_session.player1:
    #         game_session.player1 = user
    #         logger.info(f"Setting {user.username} as Player 1")
    #     elif not game_session.player2 and game_session.player1 != user:
    #         game_session.player2 = user
    #         logger.info(f"Setting {user.username} as Player 2")
    #         # Send notification that player 2 has joined
    #         async_to_sync(self.channel_layer.group_send)(
    #             self.room_group_name,
    #             {
    #                 'type': 'game_state_update',
    #                 'message': {
    #                     'type': 'game_state',
    #                     'game_status': 'accepted',
    #                     'player1_username': game_session.player1.username,
    #                     'player2_username': user.username
    #                 }
    #             }
    #         )

    #     game_session.save()
    #     return game_session

    @database_sync_to_async
    def get_username(self, user):
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
            elif message_type == 'game_accepted':
                await self.handle_game_accept(data)
            elif message_type == 'game_declined':
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
            game_id = data.get('game_id')
            
            # Get players
            player1 = await self.get_user(sender_id)
            player2 = await self.get_user(data.get('recipient_id'))
            
            # Create game session
            game_session = await create_game_session(
                game_id=game_id,
                player1=player1,
                player2=player2
            )
            
            if not game_session:
                logger.error("Failed to create game session")
                return

            # Send game state update to all players
            await self.channel_layer.group_send(
                f"pong_{game_id}", 
                {
                    'type': 'game_state_update',
                    'message': {
                        'type': 'game_state',
                        'game_status': 'accepted',
                        'player1_username': player1.username,
                        'player2_username': player2.username,
                        'game_id': game_id
                    }
                }
            )
            
            # Send direct acceptance message to sender
            await self.channel_layer.group_send(
                f"user_{sender_id}",
                {
                    'type': 'game.accept',
                    'message': {
                        'type': 'game_accepted',
                        'game_id': game_id,
                        'sender_id': sender_id,
                        'recipient_id': data.get('recipient_id'),
                        'recipient_name': data.get('recipient_name'),
                        'sender_name': data.get('sender_name'),
                        'player1_name': game_session.player1.username,
                        'player2_name': game_session.player2.username
                    }
                }
            )
            logger.info(f"Game accept notification sent to user_{sender_id}")
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

    # async def game_accept(self, event):
    #     """Handle game accept from channel layer"""
    #     try:
    #         message = event['message']
    #         # Send the acceptance message to both players
    #         await self.send(text_data=json.dumps({
    #             'type': 'game_accepted',
    #             'game_id': message['game_id'],
    #             'sender_id': message['sender_id'],
    #             'recipient_id': message['recipient_id'],
    #             'sender_name': message['sender_name'],
    #             'recipient_name': message['recipient_name'],
    #             'player1_name': message['player1_name'],
    #             'player2_name': message['player2_name']
    #         }))
            
    #         logger.info(f"Game acceptance processed for game {message['game_id']}")
    #     except Exception as e:
    #         logger.error(f"Error sending game accept: {str(e)}")
    async def game_accept(self, event):
        """Handle game accept from channel layer"""
        try:
            message = event['message']
            # Send acceptance notification to both players through game channel
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
            
            logger.info(f"Game acceptance processed for game {message['game_id']}")
        except Exception as e:
            logger.error(f"Error sending game accept: {str(e)}")

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
            logger.error(f"Error sending game decline: {str(e)}")

            