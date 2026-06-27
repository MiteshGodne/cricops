from rest_framework import viewsets
from rest_framework.response import Response
from django.db import IntegrityError
from django.utils import timezone
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
        tournament = serializer.validated_data['tournament']
        is_playing_xi = serializer.validated_data.get('is_playing_xi', True)
        squad_role = serializer.validated_data.get('squad_role', 'PLAYER')

        if tournament.status != 'ACCEPTING_APPLICATIONS' or (
            tournament.application_deadline and tournament.application_deadline < timezone.now()
        ):
            return Response({'error': 'Tournament is not accepting squad entries.'}, status=400)

        if player.current_team_id != team.team_id:
            return Response({'error': 'Player does not belong to this team.'}, status=400)

        if is_playing_xi:
            xi_count = TournamentSquad.objects.filter(
                tournament=tournament, team=team, is_playing_xi=True
            ).count()
            max_xi = tournament.regulation.players_per_side
            if xi_count >= max_xi:
                return Response({'error': f'Playing XI limit ({max_xi}) reached for this team.'}, status=400)

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