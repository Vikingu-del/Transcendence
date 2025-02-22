import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pong.models import GameSession  
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.utils import timezone

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
def create_new_game_session(player1, player2):
    """ Create a new game session and return its ID. """
    new_game = GameSession.objects.create(player1=player1, player2=player2)
    return new_game.game_id  # Return the new game session ID

@database_sync_to_async
def create_new_game_session_with_same_id(game_id, player1, player2):
    """ Deactivate the old session and create a fresh one under the same game_id. """
    GameSession.objects.filter(game_id=game_id).update(is_active=False)  # Mark old games inactive
    new_game = GameSession.objects.create(game_id=game_id, player1=player1, player2=player2)
    return new_game.id  # Return new session's primary key instead of game_id


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"pong_{self.game_id}"

        await self.accept()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print(f"Client connected and added to group {self.room_group_name}")

        # Fetch and update game session asynchronously
        game_session = await self.get_game_session()
        if not game_session:
            await self.close()
            return

        game_session = await self.assign_players(game_session)

        # Fetch updated usernames asynchronously
        player1_username = await self.get_username(game_session.player1)
        player2_username = await self.get_username(game_session.player2)

        print(f"Assigned Players: P1 -> {player1_username}, P2 -> {player2_username}")  # Debugging

        # Determine the role of the current player
        user = self.scope['user']
        player_role = 'player1' if game_session.player1 == user else 'player2' if game_session.player2 == user else None

        # Send the player's role (player1 or player2) to the client
        await self.send(text_data=json.dumps({
            'player1_username': player1_username,
            'player2_username': player2_username,
            'player_role': player_role
        }))

        # Broadcast updated player names
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_players',
                'player1_username': player1_username,
                'player2_username': player2_username
            }
        )

    async def disconnect(self, close_code):
        game_session = await self.get_game_session()
        if game_session:
            winner = await sync_to_async(lambda: game_session.player1 if game_session.player1_score > game_session.player2_score else game_session.player2)()
            await save_final_score(self.game_id, winner.username, game_session.player1_score, game_session.player2_score)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # 🏆 Handle Game Over
        if data.get('type') == 'game_over':
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
            player1 = await sync_to_async(lambda: game_session.player1)()
            player2 = await sync_to_async(lambda: game_session.player2)()
            new_game_id = await create_new_game_session_with_same_id(self.game_id, player1, player2)
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'new_game_id', 'new_game_id': str(new_game_id)}  # Convert UUID to string
            )
            return  # Exit early

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


    # 🏆 Game Over Message Handler
    async def game_over_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
            'player1_score': event['player1_score'],
            'player2_score': event['player2_score']
        }))

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
        """ Fetch the latest game session with the given game_id. """
        return GameSession.objects.filter(game_id=self.game_id).order_by('-created_at').first()


    @database_sync_to_async
    def assign_players(self, game_session):
        """ Assigns players correctly and prevents duplicate player assignment """
        user = self.scope['user']
        print(f"Connected User: {user.username}")  # Debugging

        if game_session.player1 is None:
            print(f"Setting {user.username} as Player 1")  # Debugging
            game_session.player1 = user
        elif game_session.player2 is None and game_session.player1 != user:
            print(f"Setting {user.username} as Player 2")  # Debugging
            game_session.player2 = user
        elif game_session.player1 == user:
            print(f"{user.username} is already Player 1")  # Debugging
        elif game_session.player2 == user:
            print(f"{user.username} is already Player 2")  # Debugging
        else:
            print(f"Unexpected case: P1 -> {game_session.player1.username}, P2 -> {game_session.player2.username}")  # Debugging

        game_session.save()
        return game_session  # Return the updated game session

    @database_sync_to_async
    def get_username(self, user):
        """ Safely get the username of a user object asynchronously """
        return user.username if user else "Waiting for Player 2"