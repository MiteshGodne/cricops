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
    def get_queryset(self):
        qs = super().get_queryset()
        for t in qs.filter(status='ACCEPTING_APPLICATIONS'):
            t.refresh_status()
        return qs

class TournamentOrganizerViewSet(viewsets.ModelViewSet):
    queryset = TournamentOrganizer.objects.select_related('tournament', 'user').all()
    serializer_class = TournamentOrganizerSerializer
    
    @action(detail=False, methods=['get'], url_path='open')
    def open_tournaments(self, request):
        qs = self.get_queryset().filter(
            status='ACCEPTING_APPLICATIONS', application_deadline__gt=timezone.now()
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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
    
    @action(detail=True, methods=['post'], url_path='reapply')
    def reapply(self, request, pk=None):
        application = self.get_object()
        if application.status != 'REJECTED':
            return Response({'error': 'Only rejected applications can be resubmitted.'}, status=400)
        if application.tournament.status != 'ACCEPTING_APPLICATIONS':
            return Response({'error': 'Tournament is no longer accepting applications.'}, status=400)

        application.status = 'PENDING'
        application.remarks = request.data.get('remarks', '')
        application.processed_at = None
        application.processed_by = None
        application.save(update_fields=['status', 'remarks', 'processed_at', 'processed_by'])
        return Response(ApplicationSerializer(application).data)
    
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('tournament').all()
    serializer_class = GroupSerializer

class TournamentStandingViewSet(viewsets.ModelViewSet):
    queryset = TournamentStanding.objects.select_related('tournament', 'team', 'group').all()
    serializer_class = TournamentStandingSerializer