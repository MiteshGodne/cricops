from rest_framework import serializers
from .models import Match, TeamMatch, Innings, Delivery, PlayerDelivery
from .models.deliveries import ExtraType

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class TeamMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMatch
        fields = '__all__'

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
    extra_type = serializers.ChoiceField(
        choices=ExtraType.choices if hasattr(Delivery, 'ExtraType') else [
            ('WIDE','Wide'),('NO_BALL','No Ball'),('BYE','Bye'),('LEG_BYE','Leg Bye'),('NONE','None')
        ],
        default='NONE'
    )
    extra_runs = serializers.IntegerField(default=0, min_value=0)
    wicket_type = serializers.ChoiceField(
        choices=[
            ('BOWLED','Bowled'),('CAUGHT','Caught'),('LBW','LBW'),
            ('RUN_OUT','Run Out'),('STUMPED','Stumped'),('HIT_WICKET','Hit Wicket'),('NONE','None')
        ],
        default='NONE'
    )
    fielder_id = serializers.UUIDField(required=False, allow_null=True)
    dismissed_player_id = serializers.UUIDField(required=False, allow_null=True)


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
    current_batsmen = LiveBatsmanSerializer(many=True)
    current_bowler = LiveBowlerSerializer(allow_null=True)    
    current_run_rate = serializers.FloatField()
    required_run_rate = serializers.FloatField(allow_null=True)
