from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Tournament, TournamentMatch
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# class EnrollmentCheckView(generics.RetrieveAPIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             if not request.user.is_authenticated:
#                 return Response(
#                     {'error': 'Authentication required'},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 )

#             logger.debug(f"Request user: {request.user}")
#             logger.debug(f"Request auth: {request.auth}")
            
#             user = request.user
#             tournament = Tournament.objects.filter(
#                 status="waiting", 
#                 is_active=True
#             ).first()
            
#             if not tournament:
#                 return Response({'enrolled': False})
            
#             enrolled = tournament.players.filter(id=user.id).exists()
#             return Response({'enrolled': enrolled})
            
#         except Exception as e:
#             logger.error(f"Error in check_enrollment: {str(e)}")
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
class EnrollmentCheckView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user = request.user
            # First check for any active tournament (regardless of status)
            tournament = Tournament.objects.filter(
                is_active=True
            ).first()
            
            if not tournament:
                return Response({
                    'enrolled': False,
                    'can_enroll': True,
                    'message': 'No active tournament'
                })
            
            # Check if user is already enrolled in this tournament
            is_enrolled = tournament.players.filter(id=user.id).exists()
            
            # If tournament is in progress or completed, new enrollments shouldn't be allowed
            can_enroll = tournament.status == "waiting" and not is_enrolled

            return Response({
                'enrolled': is_enrolled,
                'can_enroll': can_enroll,
                'tournament_status': tournament.status,
                'message': (
                    'Tournament in progress' if tournament.status == 'in_progress'
                    else 'Tournament completed' if tournament.status == 'completed'
                    else 'Tournament waiting for players'
                )
            })
            
        except Exception as e:
            logger.error(f"Error in check_enrollment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ActiveTournamentView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
            tournament = Tournament.objects.filter(is_active=True).first()
            
            if tournament:
                return Response({
                    'id': tournament.id,
                    'status': tournament.status,
                    'players': tournament.players.count(),
                    'max_players': tournament.max_players
                })
            return Response({'status': 'no_active_tournament'})
            
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found", "code": "user_not_found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in get_active_tournament: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TournamentEnrollView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
            tournament = Tournament.objects.filter(status="waiting", is_active=True).first()
            
            if not tournament:
                tournament = Tournament.objects.create(
                    name=f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                )
            
            success = tournament.enroll_player(user)
            
            if success:
                return Response({
                    'enrolled': True,
                    'tournament_id': tournament.id,
                    'status': tournament.status,
                    'players': tournament.players.count(),
                    'max_players': tournament.max_players
                })
            return Response({
                'enrolled': False,
                'error': 'Unable to enroll in tournament',
                'reason': 'Tournament may be full or you are already enrolled'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found", "code": "user_not_found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in enroll_tournament: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TournamentMatchesView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = get_object_or_404(Tournament, id=tournament_id)
            matches = TournamentMatch.objects.filter(tournament=tournament)
            
            matches_data = [{
                'id': match.id,
                'round': match.round,
                'player1': match.player1.username if match.player1 else None,
                'player2': match.player2.username if match.player2 else None,
                'winner': match.winner.username if match.winner else None,
                'status': match.status
            } for match in matches]
            
            return Response({
                'tournament_id': tournament_id,
                'matches': matches_data
            })
        except Exception as e:
            logger.error(f"Error in get_tournament_matches: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TournamentBracketView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id, *args, **kwargs):
        try:
            tournament = get_object_or_404(Tournament, id=tournament_id)
            
            # If tournament data is already stored, return it directly
            if hasattr(tournament, 'tournament_data') and tournament.tournament_data:
                return Response({
                    'tournament_id': tournament_id,
                    'tournament_data': tournament.tournament_data,
                    'status': tournament.status
                })
            
            # Otherwise build tournament data from matches
            matches = TournamentMatch.objects.filter(tournament=tournament).order_by('round_number', 'match_order')
            
            # Structure tournament data with semi-finals and final
            semi_finals = []
            final = None
            
            for match in matches:
                # Build match data
                match_data = {
                    'match_id': f"{'final' if match.round_number == 2 else f'semi_{match.match_order}'}",
                    'phase': 'final' if match.round_number == 2 else 'semi-final',
                    'status': match.status,
                    'winner': match.winner_id,
                    'game_id': match.game_id
                }
                
                # Add player info
                if match.player1:
                    match_data['player1'] = {
                        'id': match.player1.id,
                        'username': match.player1.username,
                        'display_name': match.player1.username
                    }
                
                if match.player2:
                    match_data['player2'] = {
                        'id': match.player2.id,
                        'username': match.player2.username,
                        'display_name': match.player2.username
                    }
                
                # Add to appropriate round
                if match.round_number == 1:
                    semi_finals.append(match_data)
                else:
                    final = match_data
            
            # Determine current phase
            current_phase = 'semi-final'
            if all(m['status'] == 'completed' for m in semi_finals if m):
                current_phase = 'final'
                if final and final['status'] == 'completed':
                    current_phase = 'completed'
            
            # Build full tournament data
            tournament_data = {
                'semi_finals': semi_finals,
                'final': final,
                'current_phase': current_phase,
                'match_scores': {}  # Initialize empty match scores
            }
            
            # Save data to tournament for future use
            tournament.tournament_data = tournament_data
            tournament.save()
            
            return Response({
                'tournament_id': tournament_id,
                'tournament_data': tournament_data,
                'status': tournament.status
            })
        except Exception as e:
            logger.error(f"Error in tournament_bracket: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompleteMatchView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, match_id, *args, **kwargs):
        try:
            match = get_object_or_404(TournamentMatch, id=match_id)
            tournament = match.tournament
            
            if request.user not in [match.player1, match.player2]:
                return Response(
                    {'error': 'You are not a participant in this match'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            winner_id = request.data.get('winner_id')
            if not winner_id:
                return Response(
                    {'error': 'Winner ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            winner = get_object_or_404(User, id=winner_id)
            if winner not in [match.player1, match.player2]:
                return Response(
                    {'error': 'Invalid winner'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            match.winner = winner
            match.status = 'completed'
            match.save()
            
            if match.round == tournament.current_round and tournament.all_matches_completed():
                tournament.status = 'completed'
                tournament.save()
            
            if tournament.status != 'completed':
                tournament.advance_tournament()
            
            return Response({
                'status': 'success',
                'match_id': match_id,
                'winner': winner.username,
                'tournament_status': tournament.status
            })
        except Exception as e:
            logger.error(f"Error in complete_match: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )