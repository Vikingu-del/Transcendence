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
        self.user = self.scope['user']

        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send initial game state
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'game_status': 'waiting',
            'host_id': self.user.id,
            'player_id': self.user.id
        }))

    async def disconnect(self, close_code):
        """Handle client disconnection"""
        try:
            # Send disconnect notification to other players
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_state_update',
                        'message': {
                            'type': 'game_state',
                            'game_status': 'ended',
                            'reason': 'disconnect',
                            'disconnected_player': str(self.user.id),
                            'message': f"{self.user.username} has left the game",
                            'score': [
                                # Send current scores from gameState
                                getattr(self, 'player_score', 0),
                                getattr(self, 'opponent_score', 0)
                            ]
                        }
                    }
                )
                
            # Remove from room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error in disconnect handler: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'paddle_move':
                await self.handle_paddle_move(data)
            elif message_type == 'ball_update':
                await self.handle_ball_update(data)
            elif message_type == 'game_start':
                await self.handle_game_start(data)
            elif message_type == 'game_end':
                await self.handle_game_end(data)
            elif message_type == 'score_update':
                await self.handle_score_update(data)

        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    async def handle_score_update(self, data):
        """Handle score updates"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_game_update',
                    'message': {
                        'type': 'score_update',
                        'score': data.get('score', [0, 0])
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error handling score update: {str(e)}")

    async def handle_game_start(self, data):
        """Handle game start"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_state_update',
                    'message': {
                        'type': 'game_state',
                        'game_status': 'started'
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error starting game: {str(e)}")

    async def handle_paddle_move(self, data):
        """Handle paddle movement with improved synchronization"""
        try:
            # Add validation for y position
            y_position = data.get('y', 0)
            y_position = max(0, min(y_position, 400))  # Assuming canvas height is 400

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_paddle',
                    'message': {
                        'type': 'paddle_move',
                        'host_id': self.scope['user'].id,
                        'y': y_position,
                        'timestamp': data.get('timestamp', 0)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error handling paddle move: {str(e)}")

    async def handle_ball_update(self, data):
        """Handle ball position updates"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_ball',
                    'message': {
                        'type': 'ball_update',
                        'ball': {
                            'x': data.get('x', 0),
                            'y': data.get('y', 0),
                            'dx': data.get('dx', 0),
                            'dy': data.get('dy', 0),
                            'radius': data.get('radius', 8)
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error handling ball update: {str(e)}")

    async def game_state_update(self, event):
        """Send game state updates to client"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'game_status': event['message']['game_status']
            }))
        except Exception as e:
            logger.error(f"Error in game state update: {str(e)}")

    async def broadcast_paddle(self, event):
        """Broadcast paddle position"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error broadcasting paddle: {str(e)}")

    async def broadcast_game_update(self, event):
        """Broadcast game updates"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error broadcasting game update: {str(e)}")

    async def broadcast_ball(self, event):
        """Broadcast ball position"""
        try:
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f"Error broadcasting ball: {str(e)}")

    async def handle_game_end(self, data):
        """Handle game end"""
        try:
            # Add a flag to check if game end has already been handled
            if hasattr(self, 'game_ended'):
                return
            self.game_ended = True  # Set the flag
            
            end_reason = data.get('reason', 'score')  # 'score' or 'disconnect'
            winner_id = data.get('winner_id')
            final_score = data.get('final_score', {})
            
            message = {
                'type': 'game_state',
                'game_status': 'ended',
            }

            if end_reason == 'disconnect':
                message.update({
                    'reason': 'disconnect',
                    'message': f"Game ended due to player disconnection",
                    'disconnected_player': data.get('disconnected_player'),
                    'winner': data.get('winner'),
                    'score': [
                        final_score.get('player1', 0),
                        final_score.get('player2', 0)
                    ]
                })
            else:  # Normal game end (score limit reached)
                player1_score = final_score.get('player1', 0)
                player2_score = final_score.get('player2', 0)
                winner = 'player1' if player1_score > player2_score else 'player2'
                
                logger.info(f"Final calculated scores - P1: {player1_score}, P2: {player2_score}")
                logger.info(f"Determined winner: {winner}")
                
                message.update({
                    'reason': 'score',
                    'message': f"Game Over! {winner.title()} wins!",
                    'winner': winner,
                    'score': [player1_score, player2_score]
                })

                logger.info(f"Sending final message to group: {message}")
                
                # Send the game end message to all players
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_state_update',
                        'message': message
                    }
                )

            # # Save the game result to the database
            # await save_game_result(
            #     self.game_id,
            #     winner_id,
            #     final_score.get('player1', 0),
            #     final_score.get('player2', 0)
            # )

        except Exception as e:
            logger.error(f"Error handling game end: {str(e)}", exc_info=True)

@database_sync_to_async
def save_game_result(game_id, winner_id, player1_score, player2_score):
    """Save only the final game result"""
    try:
        winner = User.objects.get(id=winner_id)
        GameSession.objects.create(
            game_id=game_id,
            winner=winner,
            player1_score=player1_score,
            player2_score=player2_score,
            is_active=False
        )
    except Exception as e:
        logger.error(f"Error saving game result: {str(e)}")
    