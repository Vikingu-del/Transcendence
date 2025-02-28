from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Tournament
import os
import aiohttp

import logging
logger = logging.getLogger(__name__)

class TournamentConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
        self.tournament_group = f'tournament_{self.tournament_id}'
        
        try:
            # Get token from query params
            query_string = self.scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            self.token = query_params.get('token')

            if not self.token:
                logger.error("No token provided in WebSocket connection")
                await self.close(code=4001)
                return

            # Remove 'Bearer ' prefix if present
            if self.token.startswith('Bearer '):
                self.token = self.token[7:]

            await self.channel_layer.group_add(
                self.tournament_group,
                self.channel_name
            )
            await self.accept()
            
            # Get current players and broadcast to the new connection
            players_data = await self.get_tournament_players()
            
            # Send initial state to the connecting client
            await self.send(text_data=json.dumps({
                'type': 'player_update',
                'players': players_data['players'],
                'total_players': players_data['total_players']
            }))
            
            # Broadcast to others
            await self.channel_layer.group_send(
                self.tournament_group,
                {
                    'type': 'broadcast_player_update',
                    'message': 'New player joined the tournament!',
                    'players': players_data['players']
                }
            )
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close(code=4000)
        

    async def disconnect(self, close_code):
        # Get updated players list after disconnect
        players = await self.get_tournament_players()
        
        # Notify remaining clients about the player leaving
        await self.channel_layer.group_send(
            self.tournament_group,
            {
                'type': 'broadcast_player_update',
                'players': players
            }
        )
        
        await self.channel_layer.group_discard(
            self.tournament_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data['type'] == 'match_complete':
            await self.channel_layer.group_send(
                self.tournament_group,
                {
                    'type': 'match_update',
                    'match_id': data['match_id'],
                    'winner_id': data['winner_id']
                }
            )

    async def broadcast_player_update(self, event):
        try:
            players_data = await self.get_tournament_players()
            response = {
                'type': 'player_update',
                'players': players_data['players'],
                'total_players': players_data['total_players'],
                'message': event.get('message', '')
            }

            # If we have exactly 4 players, create and broadcast tournament start
            if players_data['total_players'] == 4:
                tournament_data = await self.create_matches()
                response.update({
                    'tournament_status': 'starting',
                    'matches': tournament_data,
                    'message': 'Tournament is starting! Prepare for your matches!'
                })

            await self.send(text_data=json.dumps(response))
        except Exception as e:
            logger.error(f"Broadcast error: {str(e)}")
            await self.close(code=4000)

    async def broadcast_tournament_start(self, event):
        """Handle tournament start broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'tournament_start',
            'tournament_data': event['tournament_data'],
            'message': 'Tournament is starting! Prepare for your matches!'
        }))

    async def match_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'match_update',
            'match_id': event['match_id'],
            'winner_id': event['winner_id']
        }))

    async def get_tournament_players(self):
        try:
            tournament = await database_sync_to_async(Tournament.objects.get)(id=self.tournament_id)
            players = await database_sync_to_async(list)(tournament.players.all())
            
            # Just return basic player info without trying to fetch profiles
            player_profiles = [{
                'id': player.id,
                'username': player.username,
                'display_name': player.username  # Default to username
            } for player in players]

            return {
                'players': player_profiles,
                'total_players': len(players)
            }

        except Exception as e:
            logger.error(f"Error in get_tournament_players: {str(e)}")
            raise

    
    async def create_matches(self):
        """Create tournament matches"""
        try:
            tournament = await database_sync_to_async(Tournament.objects.get)(id=self.tournament_id)
            players = await database_sync_to_async(list)(tournament.players.all().order_by('id'))
            
            # Create semi-finals matches with consistent ordering
            semi_finals = []
            for i in range(0, 4, 2):
                semi_finals.append({
                    'match_id': f'semi_{i//2}',
                    'phase': 'semi-final',
                    'player1': {
                        'id': players[i].id,
                        'username': players[i].username,
                        'display_name': players[i].username  # Default to username
                    },
                    'player2': {
                        'id': players[i + 1].id,
                        'username': players[i + 1].username,
                        'display_name': players[i + 1].username  # Default to username
                    },
                    'status': 'pending',
                    'winner': None
                })
            
            tournament_data = {
                'semi_finals': semi_finals,
                'final': {
                    'match_id': 'final',
                    'phase': 'final',
                    'player1': None,
                    'player2': None,
                    'status': 'waiting',
                    'winner': None
                },
                'current_phase': 'semi-final'
            }

            return tournament_data
            
        except Exception as e:
            logger.error(f"Error creating matches: {str(e)}")
            raise
    
    async def store_tournament_data(self, tournament_data):
        """Store tournament data"""
        try:
            tournament = await database_sync_to_async(Tournament.objects.get)(id=self.tournament_id)
            await database_sync_to_async(setattr)(tournament, 'tournament_data', tournament_data)
            await database_sync_to_async(tournament.save)()
        except Exception as e:
            logger.error(f"Error storing tournament data: {str(e)}")
            raise

    async def get_tournament(self):
        """Get tournament instance"""
        return await database_sync_to_async(Tournament.objects.get)(id=self.tournament_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data['type'] == 'match_complete':
            await self.handle_match_complete(data)

    async def handle_match_complete(self, data):
        match_id = data['match_id']
        winner = data['winner']
        
        # Update tournament state
        tournament = await self.get_tournament()
        tournament_data = tournament.tournament_data
        
        if match_id.startswith('semi_'):
            # Handle semi-final completion
            semi_final_index = int(match_id.split('_')[1])
            tournament_data['semi_finals'][semi_final_index]['winner'] = winner
            tournament_data['semi_finals'][semi_final_index]['status'] = 'completed'
            
            # Check if all semi-finals are complete
            all_semis_complete = all(match['status'] == 'completed' 
                                   for match in tournament_data['semi_finals'])
            
            if all_semis_complete:
                # Set up final match
                winners = [match['winner'] for match in tournament_data['semi_finals']]
                tournament_data['final']['player1'] = winners[0]
                tournament_data['final']['player2'] = winners[1]
                tournament_data['final']['status'] = 'pending'
                tournament_data['current_phase'] = 'final'
        
        elif match_id == 'final':
            # Handle final completion
            tournament_data['final']['winner'] = winner
            tournament_data['final']['status'] = 'completed'
            tournament_data['current_phase'] = 'completed'
        
        # Save tournament state
        await self.update_tournament(tournament_data)
        
        # Broadcast update to all clients
        await self.channel_layer.group_send(
            self.tournament_group,
            {
                'type': 'broadcast_tournament_update',
                'tournament_data': tournament_data
            }
        )