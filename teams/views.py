from rest_framework import viewsets, serializers
from .models import Team, TournamentSquad
from .serializers import TeamSerializer, TournamentSquadSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('team_head').all()
    serializer_class = TeamSerializer

class TournamentSquadViewSet(viewsets.ModelViewSet):
    queryset = TournamentSquad.objects.select_related('player', 'team', 'tournament').all()
    serializer_class = TournamentSquadSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.validated_data['player']
        team = serializer.validated_data['team']
        if player.current_team_id != team.team_id:
            return Response({'error': 'Player does not belong to this team.'}, status=400)
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            msg = str(e)
            if 'unique_player_per_tournament' in msg:
                error = 'This player is already in a squad for this tournament (with another team).'
            elif 'unique_jersey_per_team_per_tournament' in msg:
                error = 'Jersey number already taken in this team for this tournament.'
            else:
                error = 'Could not add player to squad.'
            return Response({'error': error}, status=400)
        return Response(serializer.data, status=201)