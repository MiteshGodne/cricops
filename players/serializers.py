from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    current_team_name = serializers.CharField(source='current_team.team_name', read_only=True, default=None)
    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['player_id', 'created_at', 'updated_at']