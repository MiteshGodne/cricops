from rest_framework import serializers
from .models import Team, TournamentSquad

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['team_id', 'created_at', 'updated_at', 'created_by']
        extra_kwargs = {
            'team_name': {'required': True, 'allow_blank': False},
            'short_name': {'required': True, 'allow_blank': False},
        }

class TournamentSquadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentSquad
        fields = '__all__'
        read_only_fields = ['squad_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'application': {'required': False, 'allow_null': True}
        }