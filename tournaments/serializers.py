from rest_framework import serializers
from .models import Regulation, Tournament, TournamentOrganizer, Application, TournamentStanding, Group

class RegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = '__all__'
        read_only_fields = ['regulation_id']
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
    class Meta:
        model = TournamentOrganizer
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['application_id', 'created_at', 'updated_at', 'processed_at', 'processed_by']
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
    class Meta:
        model = TournamentStanding
        fields = '__all__'
        read_only_fields = [
            'tournament_standing_id', 'updated_at', 'matches_played', 'matches_won', 'matches_lost', 'matches_tied', 'matches_no_result', 'points', 'net_run_rate'
        ]