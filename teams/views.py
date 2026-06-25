from rest_framework import viewsets
from .models import Team, TournamentSquad
from .serializers import TeamSerializer, TournamentSquadSerializer
from matches.models.matches import TeamMatch
from matches.serializers import TeamMatchSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('team_head').all()
    serializer_class = TeamSerializer

class TeamMatchViewSet(viewsets.ModelViewSet):
    queryset = TeamMatch.objects.select_related('match', 'team').all()
    serializer_class = TeamMatchSerializer

class TournamentSquadViewSet(viewsets.ModelViewSet):
    queryset = TournamentSquad.objects.select_related('player', 'team', 'tournament').all()
    serializer_class = TournamentSquadSerializer