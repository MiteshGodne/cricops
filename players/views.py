from rest_framework import viewsets, permissions
from .models import Player
from .serializers import PlayerSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.select_related('current_team').all()
    serializer_class = PlayerSerializer
    filterset_fields = ['current_team', 'is_active']
    permission_classes = [permissions.AllowAny]