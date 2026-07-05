from rest_framework import serializers
from .models import Match, TeamMatch, Innings, Delivery, PlayerDelivery
from .models.deliveries import ExtraType, WicketType

class MatchSerializer(serializers.ModelSerializer):
    # tournament = serializers.CharField(source='tournament.tournament_id', read_only = True)
    tournament_name = serializers.ReadOnlyField(source='tournament.name')
    teams = serializers.SerializerMethodField()
    primary_umpire_email = serializers.ReadOnlyField(source='primary_umpire.email', default='No Umpire Assigned')
    class Meta:
        model = Match
        fields = '__all__'
    def get_teams(self, obj):
        from .models import TeamMatch         
        team_matches = TeamMatch.objects.filter(match=obj).select_related('team')
        return [tm.team.team_name for tm in team_matches]
    
class TeamMatchSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.team_name', read_only=True)
    class Meta:
        model = TeamMatch
        fields = '__all__'

    def get_team(self, obj):
        if obj.team:
            return {
                'team_id': str(obj.team.team_id),
                'team_name': obj.team.team_name,
                'short_name': obj.team.short_name
            }
        return None

class InningsSerializer(serializers.ModelSerializer):
    batting_team_name = serializers.CharField(source='batting_team.team_name', read_only=True)
    fielding_team_name = serializers.CharField(source='fielding_team.team_name', read_only=True)
    class Meta:
        model = Innings
        fields = '__all__'   

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'
        
class PlayerDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerDelivery
        fields = '__all__'

# for Umpire : Write serializers
class DeliveryInputSerializer(serializers.Serializer):
    innings_id = serializers.UUIDField()
    striker_id = serializers.UUIDField()
    non_striker_id = serializers.UUIDField()
    bowler_id = serializers.UUIDField()
    runs_scored = serializers.IntegerField(default=0, min_value=0, max_value=7)
    extra_type = serializers.ChoiceField(choices=ExtraType.choices, default='NONE')
    extra_runs = serializers.IntegerField(default=0, min_value=0)
    wicket_type = serializers.ChoiceField(choices=WicketType.choices, default='NONE')
    is_boundary = serializers.BooleanField(default=False)
    fielder_id = serializers.UUIDField(required=False, allow_null=True)
    dismissed_player_id = serializers.UUIDField(required=False, allow_null=True)    
    def validate(self, data):
        if data.get('extra_type') == 'NONE' and data.get('extra_runs', 0) > 0:
            raise serializers.ValidationError("extra_runs must be 0 when extra_type is NONE.")
        if data.get('extra_type') != 'NONE' and data.get('extra_runs', 0) == 0 and data.get('extra_type') in ['BYE', 'LEG_BYE']:
            raise serializers.ValidationError("extra_runs must be > 0 for BYE/LEG_BYE.")

        extra_type = data.get('extra_type', 'NONE')
        wicket_type = data.get('wicket_type', 'NONE')
        invalid_off_noball = {'BOWLED', 'CAUGHT', 'LBW', 'STUMPED', 'HIT_WICKET'}
        invalid_off_wide = {'BOWLED', 'CAUGHT', 'LBW', 'HIT_WICKET'}

        if extra_type == 'NO_BALL' and wicket_type in invalid_off_noball:
            raise serializers.ValidationError(f"{wicket_type} is not a valid dismissal off a no-ball.")
        if extra_type == 'WIDE' and wicket_type in invalid_off_wide:
            raise serializers.ValidationError(f"{wicket_type} is not a valid dismissal off a wide.")
        return data



# for Viewer : Read serializer
class LivePlayerSerializer(serializers.Serializer):
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()

class LiveBatsmanSerializer(LivePlayerSerializer):
    runs = serializers.IntegerField()
    balls_faced = serializers.IntegerField()
    fours = serializers.IntegerField()
    sixes = serializers.IntegerField()
    strike_rate = serializers.FloatField()
    is_striker = serializers.BooleanField()

class LiveBowlerSerializer(LivePlayerSerializer):
    overs = serializers.CharField()
    runs_conceded = serializers.IntegerField()
    wickets = serializers.IntegerField()
    economy = serializers.FloatField()

class LiveScoreSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    match_status = serializers.CharField()
    innings_number = serializers.IntegerField()
    batting_team = serializers.CharField()
    fielding_team = serializers.CharField()
    total_score = serializers.IntegerField()
    total_wickets = serializers.IntegerField()
    overs_completed = serializers.DecimalField(max_digits=4, decimal_places=1)
    total_extras = serializers.IntegerField()
    target_runs = serializers.IntegerField(allow_null=True)
    runs_required = serializers.IntegerField(allow_null=True)
    required_run_rate = serializers.FloatField(allow_null=True) 
    current_run_rate = serializers.FloatField()
    current_batsmen = LiveBatsmanSerializer(many=True)
    current_bowler = LiveBowlerSerializer(allow_null=True)    
    striker_id = serializers.UUIDField(allow_null=True)
    non_striker_id = serializers.UUIDField(allow_null=True)    
    bowler_id = serializers.UUIDField()
    overs_remaining = serializers.CharField(allow_null=True)
    is_paused = serializers.BooleanField()
    pause_reason = serializers.CharField(allow_blank=True)
