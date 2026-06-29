from rest_framework import viewsets
from .models import Player
from .serializers import PlayerSerializer
from core.permissions import ReadOnly, IsPlayerTeamHeadOwner, IsTeamHead

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.select_related('current_team').all()
    serializer_class = PlayerSerializer
    filterset_fields = ['current_team', 'is_active']
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [ReadOnly()]
        if self.action in ('create'):
            return [IsTeamHead()]
        return [IsPlayerTeamHeadOwner()]