from rest_framework import viewsets
from .models import Regulation, Tournament, Application, Group, TournamentStanding, TournamentOrganizer
from .serializers import RegulationSerializer, TournamentSerializer, ApplicationSerializer, GroupSerializer, TournamentStandingSerializer, TournamentOrganizerSerializer
from django.utils import timezone
from teams.models import TournamentSquad
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('regulation', 'created_by').all()
    serializer_class = TournamentSerializer

class TournamentOrganizerViewSet(viewsets.ModelViewSet):
    queryset = TournamentOrganizer.objects.select_related('tournament', 'user').all()
    serializer_class = TournamentOrganizerSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('team', 'tournament').all()
    serializer_class = ApplicationSerializer
    def perform_update(self, serializer):
        old_status = serializer.instance.status
        if 'status' in serializer.validated_data:
            app = serializer.save(processed_at=timezone.now())
        else:
            app = serializer.save()

        if old_status != 'ACCEPTED' and app.status == 'ACCEPTED':
            TournamentStanding.objects.get_or_create(
                tournament=app.tournament, team=app.team
            )
            
    @action(detail=False, methods=['post'], url_path='submit-application')
    def submit_application(self, request):
        team_id = request.data.get('team_id')
        tournament_id = request.data.get('tournament_id')
        registered_name = request.data.get('registered_name')
        registered_short_name = request.data.get('registered_short_name')
        tournament = Tournament.objects.select_related('regulation').get(tournament_id=tournament_id)
        squad_qs = TournamentSquad.objects.filter(
            tournament_id=tournament_id, team_id=team_id, application__isnull=True
        )
        min_required = tournament.regulation.players_per_side
        if squad_qs.count() < min_required:
            return Response(
                {'error': f'At least {min_required} players required, found {squad_qs.count()}'},
                status=400
            )

        try:
            application = Application.objects.create(
                team_id=team_id, tournament_id=tournament_id,
                registered_name=registered_name, registered_short_name=registered_short_name
            )
        except IntegrityError as e:
            msg = str(e)
            if 'unique_team_tournament_application' in msg:
                error = 'This team has already applied to this tournament.'
            elif 'unique_team_name_per_tournament' in msg:
                error = 'registered_name already taken in this tournament.'
            elif 'unique_short_name_per_tournament' in msg:
                error = 'registered_short_name already taken in this tournament.'
            else:
                error = 'Could not create application.'
            return Response({'error': error}, status=400)
        
        squad_qs.update(application=application)
        return Response({'application_id': application.application_id, 'players_linked': squad_qs.count()}, status=201)
    
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('tournament').all()
    serializer_class = GroupSerializer

class TournamentStandingViewSet(viewsets.ModelViewSet):
    queryset = TournamentStanding.objects.select_related('tournament', 'team', 'group').all()
    serializer_class = TournamentStandingSerializer