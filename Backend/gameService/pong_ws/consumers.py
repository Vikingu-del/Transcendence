from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pong.models import GameSession  # Import your GameSession model

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        print(f"🔍 [DEBUG] Connecting WebSocket: {self.user} (Authenticated: {self.user.is_authenticated})")

        if not self.user.is_authenticated:
            print("🚫 [DEBUG] Closing WebSocket (unauthenticated user)")
            await self.close()
            return

        try:
            self.game_session = await sync_to_async(GameSession.objects.get)(id=self.game_id)
        except GameSession.DoesNotExist:
            print(f"❌ [DEBUG] GameSession {self.game_id} not found")
            await self.close()
            return

        player1 = await sync_to_async(lambda: self.game_session.player1.id if self.game_session.player1 else None)()
        player2 = await sync_to_async(lambda: self.game_session.player2.id if self.game_session.player2 else None)()

        if not player2 and self.user.id != player1:
            await sync_to_async(lambda: setattr(self.game_session, "player2", self.user))()
            await sync_to_async(self.game_session.save)()
            player2 = self.user.id  # Update variable after setting

        print(f"📌 [DEBUG] Player1: {player1}, Player2: {player2}, Current User: {self.user.id}")

        if player1 != self.user.id and player2 != self.user.id:
            print(f"🚫 [DEBUG] User {self.user} is not part of this game.")
            await self.close()
            return

        if self.user.id == player1:
            self.player_number = 1
        elif self.user.id == player2:
            self.player_number = 2
        else:
            print(f"🚫 [DEBUG] User {self.user} is not part of this game.")
            await self.close()
            return

        self.room_group_name = f"pong_{self.game_id}"

        # ✅ Accept connection BEFORE group add (important)
        await self.accept()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print(f"✅ [DEBUG] WebSocket accepted for {self.user}")

        game_state = await sync_to_async(self.game_session.get_game_state)()

        await self.send(text_data=json.dumps({
            'message': 'You have joined the game!',
            'player_number': self.player_number, 
            'game_state': game_state,
        }))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_update',
                'game_state': game_state
            }
    )


    async def disconnect(self, close_code):
        """Remove player from group only if they were added."""
        if hasattr(self, 'room_group_name'):  # Ensure attribute exists
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def game_state_update(self, event):
        """Send updated game state to both players."""
        await self.send(text_data=json.dumps({
            'game_state': event['game_state']
        }))

    async def update_game_state(self, player, new_paddle_position):
        """Update the player's paddle position and broadcast the game state."""
        print(f"🎮 [DEBUG] Player {player} moved paddle to {new_paddle_position}")

        if player == 1:
            print(f"🛠 [DEBUG] Updating Player 1 paddle position")
            self.game_session.player1_paddle = new_paddle_position
        elif player == 2:
            print(f"🛠 [DEBUG] Updating Player 2 paddle position")
            self.game_session.player2_paddle = new_paddle_position
        else:
            print(f"❌ [DEBUG] Invalid player {player} trying to move a paddle!")

        await sync_to_async(self.game_session.save)()
        await sync_to_async(self.game_session.refresh_from_db)()

        game_state = await sync_to_async(self.game_session.get_game_state)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_update',
                'game_state': game_state
            }
        )


    async def receive(self, text_data):
        data = json.loads(text_data)

        print(f"📩 [DEBUG] Received WebSocket message: {data}")

        if data['type'] == 'move_paddle':
            new_paddle_position = data['new_position']

            # Use self.player_number instead of trusting frontend data
            await self.update_game_state(self.player_number, new_paddle_position)


