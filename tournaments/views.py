from rest_framework import viewsets
from .models import Regulation, Tournament, Application, Group, TournamentStanding, TournamentOrganizer
from .serializers import RegulationSerializer, TournamentSerializer, ApplicationSerializer, GroupSerializer, TournamentStandingSerializer, TournamentOrganizerSerializer
from django.utils import timezone
from teams.models import TournamentSquad
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from core.permissions import IsOrganizer, IsCreatorOwner, ReadOnly, IsOrganizerOwner, IsTeamHead, IsGroupTournamentOwner, IsTournamentOrganizer, IsOwnTeamHead

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.select_related('created_by').all()
    serializer_class = RegulationSerializer
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOrganizer(), IsCreatorOwner()]
        return [IsOrganizer()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        reg = serializer.instance
        ongoing = reg.tournaments.filter(status__in=['ONGOING','COMPLETED']).exists()
        if ongoing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Cannot edit regulation — tournament is already ongoing.')
        serializer.save()
    

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('regulation', 'created_by').all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOrganizer(), IsOrganizerOwner()]
        return [IsOrganizer()] 
        
    def perform_create(self, serializer):
        tournament = serializer.save(created_by=self.request.user)
        TournamentOrganizer.objects.create(
            tournament=tournament,
            user=self.request.user,
            is_primary=True
        )
        
def perform_update(self, serializer):
    old_status = self.get_object().status
    tournament = serializer.save()
    if tournament.status == 'COMPLETED' and old_status != 'COMPLETED':
        top_standing = TournamentStanding.objects.filter(
            tournament=tournament
        ).order_by('-points', '-net_run_rate').first()
        if top_standing:
            tournament.winner_team = top_standing.team
            tournament.save(update_fields=['winner_team'])
        
    def get_queryset(self):
        qs = super().get_queryset()
        for t in qs.filter(status='ACCEPTING_APPLICATIONS'):
            t.refresh_status()
        return qs

class TournamentOrganizerViewSet(viewsets.ModelViewSet):
    queryset = TournamentOrganizer.objects.select_related('tournament', 'user').all()
    serializer_class = TournamentOrganizerSerializer
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        return [IsTournamentOrganizer()]
    
    @action(detail=False, methods=['get'], url_path='open')
    def open_tournaments(self, request):
        qs = Tournament.objects.filter(
            status='ACCEPTING_APPLICATIONS', application_deadline__gt=timezone.now()
        )
        serializer = TournamentSerializer(qs, many=True)
        return Response(serializer.data)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('team', 'tournament').all()
    serializer_class = ApplicationSerializer
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action == 'submit_application':
            return [IsTeamHead()]
        if self.action == 'reapply':
            return [IsTeamHead()]
        if self.action == 'withdraw':
            return [IsOwnTeamHead()]
        return [IsTournamentOrganizer()]
    
    def get_queryset(self):
        qs = Application.objects.select_related('team','tournament').all()
        team = self.request.query_params.get('team')
        tournament = self.request.query_params.get('tournament')
        status = self.request.query_params.get('status')
        if team: qs = qs.filter(team__team_id=team)
        if tournament: qs = qs.filter(tournament__tournament_id=tournament)
        if status: qs = qs.filter(status=status)
        return qs
    
    def perform_update(self, serializer):
        old_status = serializer.instance.status
        if 'status' in serializer.validated_data:
            app = serializer.save(processed_at=timezone.now(),processed_by=self.request.user)
        else:
            app = serializer.save()
        if old_status != 'ACCEPTED' and app.status == 'ACCEPTED':
            TournamentStanding.objects.get_or_create(tournament=app.tournament, team=app.team)

            
    @action(detail=False, methods=['post'], url_path='submit-application')
    def submit_application(self, request):
        team_id = request.data.get('team_id')
        tournament_id = request.data.get('tournament_id')
        registered_name = request.data.get('registered_name')
        registered_short_name = request.data.get('registered_short_name')
        try:
            tournament = Tournament.objects.select_related('regulation').get(tournament_id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({'error': 'Invalid tournament_id.'}, status=400)     
        from teams.models import Team
        user_teams = Team.objects.filter(team_head=request.user).values_list('team_id', flat=True)
        existing = Application.objects.filter(tournament_id=tournament_id, team_id__in=user_teams,status__in=['PENDING', 'ACCEPTED']).exclude(team_id=team_id).first()
        if existing:
            return Response({
                'error': f'You already have a team ({existing.team.team_name}) applied/accepted in this tournament. One team per organizer per tournament.'
            }, status=400)
        squad_qs = TournamentSquad.objects.filter(
            tournament_id=tournament_id, team_id=team_id, application__isnull=True
        )
        min_required = tournament.regulation.players_per_side
        if squad_qs.count() < min_required:
            return Response(
                {'error': f'At least {min_required} players required, found {squad_qs.count()} in your squad.'},
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
        
        count = squad_qs.count()         
        squad_qs.update(application=application)
        return Response({'application_id': application.application_id, 'players_linked': count}, status=201)
    
    @action(detail=True, methods=['post'], url_path='reapply')
    def reapply(self, request, pk=None):
        application = self.get_object()
        if application.status != 'REJECTED' and application.status != 'WITHDRAWN':
            return Response({'error': 'Only rejected applications can be resubmitted.'}, status=400)
        if application.tournament.status != 'ACCEPTING_APPLICATIONS':
            return Response({'error': 'Tournament is no longer accepting applications.'}, status=400)

        application.status = 'PENDING'
        application.remarks = request.data.get('remarks', '')
        application.processed_at = None
        application.processed_by = None
        application.save(update_fields=['status', 'remarks', 'processed_at', 'processed_by'])
        return Response(ApplicationSerializer(application).data)
    @action(detail=True, methods=['post'], url_path='withdraw')
    def withdraw(self, request, pk=None):
        application = self.get_object()
        if application.team.team_head != request.user:
            return Response({'error': 'You do not own this application.'}, status=403)
        if application.status not in ['PENDING', 'ACCEPTED']:
            return Response({'error': 'Only PENDING or ACCEPTED applications can be withdrawn.'}, status=400)
        application.status = 'WITHDRAWN'
        application.processed_at = timezone.now()
        application.processed_by = request.user
        application.save(update_fields=['status', 'processed_at', 'processed_by'])
        return Response(ApplicationSerializer(application).data)
    
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('tournament').all()
    serializer_class = GroupSerializer
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOrganizer(), IsGroupTournamentOwner()]
        return [IsOrganizer()]

class TournamentStandingViewSet(viewsets.ModelViewSet):
    queryset = TournamentStanding.objects.select_related('tournament', 'team', 'group').all()
    serializer_class = TournamentStandingSerializer
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        return []