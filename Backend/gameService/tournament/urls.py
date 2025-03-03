from django.urls import path
from . import views

urlpatterns = [
    path('check-enrollment/', views.EnrollmentCheckView.as_view(), name='check_enrollment'),
    path('active/', views.ActiveTournamentView.as_view(), name='active_tournament'),
    path('enroll/', views.TournamentEnrollView.as_view(), name='enroll_tournament'),
    path('<int:tournament_id>/matches/', views.TournamentMatchesView.as_view(), name='tournament_matches'),
    path('<int:tournament_id>/bracket/', views.TournamentBracketView.as_view(), name='tournament_bracket'),
    path('match/<int:match_id>/complete/', views.CompleteMatchView.as_view(), name='complete_match'),
    path('local-tournament/', views.CreateLocalTournamentView.as_view(), name='create-local-tournament')
]