from rest_framework import serializers
from .models import Regulation, Tournament, TournamentOrganizer, Application, TournamentStanding, Group

class RegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = '__all__'
        read_only_fields = ['regulation_id', 'created_by']
    def validate(self, data):
        instance_data = {
            k: v for k, v in self.instance.__dict__.items()
            if not k.startswith('_')
        } if self.instance else {}
        instance = Regulation(**{**instance_data, **data})
        instance.clean()
        return data

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'
        read_only_fields = ['tournament_id', 'created_at', 'updated_at', 'created_by']

class TournamentOrganizerSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_fname = serializers.CharField(source='user.first_name', read_only=True)
    user_lname = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = TournamentOrganizer
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']

class ApplicationSerializer(serializers.ModelSerializer):
    team = serializers.ReadOnlyField(source='team.team_id')
    tournament_name = serializers.ReadOnlyField(source='tournament.name')
    team_name = serializers.ReadOnlyField(source='team.team_name')
    team_head_fname = serializers.ReadOnlyField(source='team.team_head.first_name')
    team_head_lname = serializers.ReadOnlyField(source='team.team_head.last_name')
    processed_by_email = serializers.ReadOnlyField(source="processed_by.email")
    processed_by_name = serializers.ReadOnlyField(source="processed_by.first_name")
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['application_id', 'created_at', 'updated_at', 'processed_at', 'processed_by', 'team']
        extra_kwargs = {
            'registered_name': {'required': True, 'allow_blank': False},
            'registered_short_name': {'required': True, 'allow_blank': False},
        }

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['group_id']

class TournamentStandingSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.team_name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    class Meta:
        model = TournamentStanding
        fields = '__all__'
        read_only_fields = [
            'tournament_standing_id', 'updated_at', 'matches_played', 'matches_won', 'matches_lost', 'matches_tied', 'matches_no_result', 'points', 'net_run_rate'
        ]