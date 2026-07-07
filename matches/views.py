from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from .models import Match, Innings, MatchLiveState, TeamMatch, Delivery, PlayerDelivery
from .serializers import MatchSerializer, InningsSerializer, DeliveryInputSerializer, LiveScoreSerializer, TeamMatchSerializer, DeliverySerializer, PlayerDeliverySerializer
from .services import process_delivery, get_live_score, update_standings
from tournaments.models import Application
from core.permissions import ReadOnly, IsOrganizer, IsMatchOrganizerOwner, IsUmpireForMatch, AllowAny, IsUmpireForMatchFromURL

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related('tournament', 'venue', 'winner_team', 'primary_umpire').all()
    serializer_class = MatchSerializer
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action in ('update', 'partial_update', 'destroy', 'abandon'):
            return  [IsOrganizer(), IsMatchOrganizerOwner()]
        if self.action in ('assign_umpire',):
            return  [IsOrganizer(), IsMatchOrganizerOwner()]
        return [IsOrganizer()] 

    def get_object(self):
        obj = super().get_object()
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS'):
            self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=True, methods=['post'], url_path='abandon', permission_classes=[IsOrganizer, IsMatchOrganizerOwner])
    def abandon(self, request, pk=None):
        match = self.get_object()
        match.status = 'ABANDONED'
        match.result_type = 'ABANDONED'
        match.result_note = request.data.get('reason', '')
        match.save(update_fields=['status', 'result_type', 'result_note'])
        match.standings_applied = False
        update_standings(match)  
        return Response({'status': 'match abandoned'})

    @action(detail=True, methods=['post'], url_path='assign-umpire', permission_classes=[IsOrganizer, IsMatchOrganizerOwner])
    def assign_umpire(self, request, pk=None):
        match = self.get_object()
        email = request.data.get('email')
        try:
            from accounts.models import User
            umpire = User.objects.get(email=email, apply_for='UMPIRE', role='PENDING')
        except User.DoesNotExist:
            return Response({'error': 'No pending umpire applicant with that email.'}, status=400)
        match.primary_umpire = umpire
        match.save(update_fields=['primary_umpire'])
        umpire.role = 'UMPIRE'
        umpire.save(update_fields=['role'])
        return Response({'assigned': str(umpire.user_id), 'email': umpire.email})
    
    def perform_create(self, serializer):
        match = serializer.save()
        match.innings_count = match.tournament.regulation.innings_per_team * 2
        match.save(update_fields=['innings_count'])

class InningsViewSet(viewsets.ModelViewSet):
    queryset = Innings.objects.select_related('match', 'batting_team', 'fielding_team').all()
    serializer_class = InningsSerializer
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        return [IsOrganizer()] 
    
class TeamMatchViewSet(viewsets.ModelViewSet):
    queryset = TeamMatch.objects.select_related('match', 'team').all()
    serializer_class = TeamMatchSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        match_id = self.request.query_params.get('match')
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action == 'submit_toss':
            return [IsUmpireForMatchFromURL()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOrganizer()]
        return [IsOrganizer()]  
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.validated_data['match']
        team = serializer.validated_data['team']
        accepted = Application.objects.filter(tournament=match.tournament, team=team, status='ACCEPTED').exists()
        if not accepted:
            return Response({'error': 'Team application not ACCEPTED for this tournament.'}, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=['post'], url_path='submit-toss', permission_classes=[IsUmpireForMatchFromURL])  
    def submit_toss(self, request):
        try:
            match_id = request.data.get('match_id')
            toss_winner_team_id = str(request.data.get('toss_winner_team_id', '')).strip().lower()
            toss_decision = request.data.get('toss_decision')

            try:
                match = Match.objects.select_related('tournament').get(match_id=match_id)
            except Match.DoesNotExist:
                return Response({'error': 'Match not found.'}, status=404)

            if match.tournament.created_by != request.user and match.primary_umpire != request.user:
                return Response({'error': 'You are neither the tournament organizer nor the assigned umpire for this match.'}, status=403)

            team_matches = TeamMatch.objects.filter(match_id=match_id).select_related('team')
            if team_matches.count() != 2:
                return Response({'error': f'Both teams not added to match. Found {team_matches.count()} entries.'}, status=400)

            winner_tm = None
            for tm in team_matches:
                if str(tm.team.pk).lower() == toss_winner_team_id:
                    winner_tm = tm
                    break

            if not winner_tm:
                return Response({'error': f'Selected toss winner team ID ({toss_winner_team_id}) is not linked to this match.'}, status=400)

            loser_tm = team_matches.exclude(id=winner_tm.id).first()

            winner_tm.is_toss_winner = True
            winner_tm.toss_decision = toss_decision
            winner_tm.save(update_fields=['is_toss_winner', 'toss_decision'])

            batting_team = winner_tm.team if toss_decision == 'BAT' else loser_tm.team
            fielding_team = loser_tm.team if toss_decision == 'BAT' else winner_tm.team

            # Initialize Innings
            innings1, _ = Innings.objects.get_or_create(
                match_id=match_id, innings_number=1,
                defaults={'batting_team': batting_team, 'fielding_team': fielding_team}
            )

            # Initialize or update MatchLiveState
            MatchLiveState.objects.update_or_create(
                match=match,
                defaults={'current_innings': innings1}
            )

            match.status = 'LIVE'
            match.save(update_fields=['status'])

            return Response({'innings_id': str(innings1.innings_id), 'batting_team': batting_team.team_name}, status=200)

        except Exception as e:
            return Response({'error': f'Internal Server Error: {str(e)}'}, status=500)
    
class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Delivery.objects.select_related('innings', 'match').all()
    serializer_class = DeliverySerializer
    permission_classes = [ReadOnly]

class PlayerDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlayerDelivery.objects.select_related('player', 'delivery').all()
    serializer_class = PlayerDeliverySerializer
    permission_classes = [ReadOnly]

@api_view(['POST'])
@permission_classes([IsUmpireForMatch])
def submit_delivery(request):
    serializer = DeliveryInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        innings = Innings.objects.select_related('match').get(innings_id=serializer.validated_data['innings_id'])
        if innings.match.is_paused:
            return Response({'error': 'Match is paused.'}, status=status.HTTP_400_BAD_REQUEST)
        delivery = process_delivery(serializer.validated_data)
        return Response({
            'status': 'delivery recorded',
            'delivery_id': delivery.delivery_id,
            'ball_sequence': delivery.ball_sequence,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def live_score(request, match_id):
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

    if match.status not in ['LIVE', 'COMPLETED']:
        return Response(
            {'error': 'Match is not live'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        payload = get_live_score(match)
        serializer = LiveScoreSerializer(payload)
        return Response(serializer.data)
    except MatchLiveState.DoesNotExist:
        return Response(
            {'error': 'Live state not initialized'},
            status=status.HTTP_404_NOT_FOUND
        )
        
@api_view(['POST'])
@permission_classes([IsUmpireForMatchFromURL])
def swap_striker(request, match_id):
    try:
        live_state = MatchLiveState.objects.get(match_id=match_id)
    except MatchLiveState.DoesNotExist:
        return Response({'error': 'Live state not found'}, status=404)
    live_state.current_striker, live_state.current_non_striker = (live_state.current_non_striker, live_state.current_striker)
    live_state.save(update_fields=['current_striker', 'current_non_striker'])
    return Response({'striker': live_state.current_striker_id, 'non_striker': live_state.current_non_striker_id})

@api_view(['POST'])
@permission_classes([IsOrganizer])
def approve_umpire(request):
    user_id = request.data.get('user_id')
    try:
        from accounts.models import User
        umpire = User.objects.get(user_id=user_id, apply_for='UMPIRE', role='PENDING')
    except User.DoesNotExist:
        return Response({'error': 'No pending umpire applicant with that user_id.'}, status=400)
    umpire.role = 'UMPIRE'
    umpire.save(update_fields=['role'])
    return Response({'approved': str(umpire.user_id), 'role': umpire.role})

@api_view(['POST'])
@permission_classes([IsUmpireForMatchFromURL])
def resume_match(request, match_id):
    match = Match.objects.get(match_id=match_id)
    match.is_paused = False
    match.pause_reason = ''
    match.save(update_fields=['is_paused', 'pause_reason'])
    live_state = MatchLiveState.objects.get(match=match)
    live_state.current_striker_id = request.data.get('striker_id') or live_state.current_striker_id
    live_state.current_non_striker_id = request.data.get('non_striker_id') or live_state.current_non_striker_id
    live_state.current_bowler_id = request.data.get('bowler_id') or live_state.current_bowler_id
    live_state.save(update_fields=['current_striker','current_non_striker','current_bowler'])
    return Response({'is_paused': False})

@api_view(['POST'])
@permission_classes([IsUmpireForMatchFromURL])
def pause_match(request, match_id):
    match = Match.objects.get(match_id=match_id)
    match.is_paused = True
    match.pause_reason = 'MANUAL'
    match.save(update_fields=['is_paused', 'pause_reason'])
    return Response({'is_paused': True})