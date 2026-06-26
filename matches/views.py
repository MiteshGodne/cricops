from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Match, Innings, MatchLiveState, TeamMatch
from .serializers import MatchSerializer, InningsSerializer, DeliveryInputSerializer, LiveScoreSerializer, TeamMatchSerializer
from .services import process_delivery, get_live_score

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related('tournament', 'venue', 'winner_team', 'primary_umpire').all()
    serializer_class = MatchSerializer

class InningsViewSet(viewsets.ModelViewSet):
    queryset = Innings.objects.select_related('match', 'batting_team', 'fielding_team').all()
    serializer_class = InningsSerializer
    
class TeamMatchViewSet(viewsets.ModelViewSet):
    queryset = TeamMatch.objects.select_related('match', 'team').all()
    serializer_class = TeamMatchSerializer


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def submit_delivery(request):
    serializer = DeliveryInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        delivery = process_delivery(serializer.validated_data)
        return Response({
            'status': 'delivery recorded',
            'delivery_id': delivery.delivery_id,
            'ball_sequence': delivery.ball_sequence,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
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