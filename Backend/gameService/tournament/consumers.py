from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Tournament
import os
import aiohttp
import uuid

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
            logger.debug(f"Initial players data: {players_data}")
            
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
        logger.debug(f"Disconnecting with code: {close_code}")
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
        logger.debug(f"Received message: {text_data}")
        try:
            data = json.loads(text_data)
            
            if data['type'] == 'match_complete':
                logger.info(f"Processing match_complete message: {data}")
                await self.handle_match_complete(data)
            else:
                logger.warning(f"Unknown message type: {data.get('type')}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON: {text_data}")
        except KeyError:
            logger.error(f"Missing 'type' in message: {text_data}")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)

    async def broadcast_player_update(self, event):
        try:
            players_data = await self.get_tournament_players()
            logger.debug(f"Broadcasting player update: {players_data}")
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
        logger.debug(f"Broadcasting tournament start: {event['tournament_data']}")
        await self.send(text_data=json.dumps({
            'type': 'tournament_start',
            'tournament_data': event['tournament_data'],
            'message': 'Tournament is starting! Prepare for your matches!'
        }))

    async def match_update(self, event):
        logger.debug(f"Match update: {event}")
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
                    'winner': None,
                    'game_id': str(uuid.uuid4())  # Generate a unique game ID
                })
            
            tournament_data = {
                'semi_finals': semi_finals,
                'final': {
                    'match_id': 'final',
                    'phase': 'final',
                    'player1': None,
                    'player2': None,
                    'status': 'waiting',
                    'winner': None,
                    'game_id': str(uuid.uuid4())  # Generate a unique game ID for the final
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

    async def handle_match_complete(self, data):
        try:
            match_id = data['match_id']
            winner_id = data['winner_id'] 
            
            # Log received data for debugging
            logger.info(f"Received match_complete with match_id={match_id}, winner_id={winner_id}")
            
            # Make sure winner_id is an integer if it's not None
            if winner_id is not None:
                winner_id = int(winner_id)
            
            # Update tournament state
            tournament = await self.get_tournament()
            tournament_data = tournament.tournament_data
            
            # Validate tournament data structure
            if not tournament_data:
                logger.error("Tournament data is empty - initializing it now")
                # Initialize tournament data if empty
                tournament_data = await self.create_matches()
                await self.store_tournament_data(tournament_data)
            
            # Process the semi-final match
            if match_id.startswith('semi_'):
                semi_final_index = int(match_id.split('_')[1])
                
                # Check if index is valid
                if semi_final_index >= len(tournament_data['semi_finals']):
                    logger.error(f"Invalid semi-final index: {semi_final_index}")
                    return
                    
                # Update the winner
                tournament_data['semi_finals'][semi_final_index]['winner'] = winner_id
                tournament_data['semi_finals'][semi_final_index]['status'] = 'completed'
                
                # Store match score if provided
                if 'final_score' in data:
                    if not tournament_data.get('match_scores'):
                        tournament_data['match_scores'] = {}
                    tournament_data['match_scores'][match_id] = data['final_score']
                
                # Check if both semi-finals are complete to set up the final
                completed_semis = [m for m in tournament_data['semi_finals'] if m.get('status') == 'completed']
                
                # Only advance to finals if BOTH semi-finals are completed
                if len(completed_semis) == 2 and len(tournament_data['semi_finals']) == 2:
                    # Update tournament phase
                    tournament_data['current_phase'] = 'final'
                    
                    # Get winners from semi-finals
                    semi_winners = []
                    for semi in tournament_data['semi_finals']:
                        if semi.get('winner') is not None:
                            # Find the player object that matches the winner ID
                            winner_data = None
                            if semi.get('player1', {}).get('id') == semi.get('winner'):
                                winner_data = semi.get('player1')
                            elif semi.get('player2', {}).get('id') == semi.get('winner'):
                                winner_data = semi.get('player2')
                            
                            if winner_data:
                                semi_winners.append(winner_data)
                    
                    # If we have two winners, set them in the final match
                    if len(semi_winners) == 2:
                        tournament_data['final']['player1'] = semi_winners[0]
                        tournament_data['final']['player2'] = semi_winners[1]
                        tournament_data['final']['status'] = 'pending'
                        
                        logger.info(f"Both semi-finals completed, setting up final match between {semi_winners[0].get('username')} and {semi_winners[1].get('username')}")
                    else:
                        logger.error(f"Cannot set up final: Expected 2 semi-final winners, but got {len(semi_winners)}")
                else:
                    logger.info(f"Waiting for other semi-final to complete. Completed: {len(completed_semis)}/{len(tournament_data['semi_finals'])}")
                    tournament_data['current_phase'] = 'semi-final'  # Ensure it stays in semi-final phase

            # Process the final match
            elif match_id == 'final':
                # Update the final match with winner
                tournament_data['final']['winner'] = winner_id
                tournament_data['final']['status'] = 'completed'
                
                # Store match score if provided
                if 'final_score' in data:
                    if not tournament_data.get('match_scores'):
                        tournament_data['match_scores'] = {}
                    tournament_data['match_scores'][match_id] = data['final_score']
                
                # Update tournament status to completed
                tournament_data['current_phase'] = 'completed'
                
                # Find the winner's username for display
                winner_username = "Unknown"
                if tournament_data['final'].get('player1', {}).get('id') == winner_id:
                    winner_username = tournament_data['final'].get('player1', {}).get('username', "Unknown")
                elif tournament_data['final'].get('player2', {}).get('id') == winner_id:
                    winner_username = tournament_data['final'].get('player2', {}).get('username', "Unknown")
                
                # Update tournament status in the database
                tournament_data['champion'] = {
                    'id': winner_id,
                    'username': winner_username
                }
                
                # Update tournament status in the database
                await database_sync_to_async(self.update_tournament_status)(tournament.id, 'completed', winner_id)
                
                logger.info(f"Tournament completed! Champion: {winner_username} (ID: {winner_id})")
            
            # Save updated tournament data
            await self.store_tournament_data(tournament_data)
            
            # Broadcast the update to all clients
            await self.channel_layer.group_send(
                self.tournament_group,
                {
                    'type': 'broadcast_tournament_update',
                    'tournament_data': tournament_data
                }
            )
            
        except KeyError as e:
            logger.error(f"Missing key in match_complete data: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling match completion: {str(e)}", exc_info=True)

    @database_sync_to_async
    def update_tournament_status(self, tournament_id, status, winner_id=None):
        """Update tournament status in database"""
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.status = status
            if winner_id:
                tournament.winner_id = winner_id
            tournament.save()
            logger.info(f"Updated tournament {tournament_id} status to {status}")
            return True
        except Tournament.DoesNotExist:
            logger.error(f"Tournament {tournament_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating tournament status: {str(e)}")
            return False

    async def broadcast_tournament_update(self, event):
        """Broadcast tournament updates to clients"""
        try:
            tournament_data = event['tournament_data']
            await self.send(text_data=json.dumps({
                'type': 'tournament_update',
                'tournament_data': tournament_data
            }))
        except Exception as e:
            logger.error(f"Error broadcasting tournament update: {str(e)}")

    async def update_tournament(self, tournament_data):
        """Update tournament data in the database"""
        try:
            tournament = await database_sync_to_async(Tournament.objects.get)(id=self.tournament_id)
            # Ensure 'tournament_data' field exists or handle it appropriately
            tournament.tournament_data = tournament_data  # This line assumes 'tournament_data' is a valid field
            await database_sync_to_async(tournament.save)()
        except Exception as e:
            logger.error(f"Error updating tournament data: {str(e)}")
            raise