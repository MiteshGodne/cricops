from django.db import models
from django.core.exceptions import ValidationError

class MatchFormat(models.TextChoices):
    T20 = 'T20', 'T20'
    ODI = 'ODI', 'ODI'
    TEST = 'TEST', 'Test'
    T10 = 'T10', 'T10'
    CUSTOM = 'CUSTOM', 'Custom'
    
class TiebreakerMethod(models.TextChoices):
    NET_RUN_RATE = 'NRR', 'Net Run Rate'
    HEAD_TO_HEAD = 'H2H', 'Head to Head'
    BOWL_OUT = 'BOWL_OUT', 'Bowl Out'
    SUPER_OVER = 'SUPER_OVER', 'Super Over'
    MOST_WINS = 'MOST_WINS', 'Most Wins'

class TournamentFormat(models.TextChoices):
    LEAGUE = 'LEAGUE', 'League (Round Robin)'
    KNOCKOUT = 'KNOCKOUT', 'Knockout'
    GROUP_KNOCKOUT = 'GROUP_KNOCKOUT', 'Group Stage + Knockout'
    DOUBLE_ELIMINATION = 'DOUBLE_ELIMINATION', 'Double Elimination'


class Regulation(models.Model):
    regulation_id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey("accounts.User", verbose_name="created_by", on_delete=models.CASCADE, related_name="regulator")

    ''' Match rules '''
    match_format = models.CharField(max_length=10, choices=MatchFormat.choices, default=MatchFormat.T20)
    overs_per_innings = models.SmallIntegerField(null=True, blank=True)  
    innings_per_team = models.SmallIntegerField(default=1) 
    max_overs_per_bowler = models.SmallIntegerField(null=True, blank=True)
    max_bouncers_per_over = models.SmallIntegerField(default=0)
    players_per_side = models.SmallIntegerField(default=11)
    wide_value = models.SmallIntegerField(default=1)
    noball_free_hit_enabled = models.BooleanField(default=True)
    noball_value = models.SmallIntegerField(default=1)
    powerplay_config = models.JSONField(default=dict)
    drs_per_innings = models.SmallIntegerField(default=2)
    timed_out_limit = models.SmallIntegerField(default=180) # seconds
    super_over_enabled = models.BooleanField(default=False)
    custom_regulations = models.JSONField(default=dict)

    ''' Tournament structure rules '''
    tournament_format = models.CharField(max_length=20, choices=TournamentFormat.choices, default=TournamentFormat.LEAGUE)
    teams_per_group = models.SmallIntegerField(null=True, blank=True)
    teams_qualifying_per_group = models.SmallIntegerField(null=True, blank=True)
    min_teams = models.SmallIntegerField(default=2)
    max_teams = models.SmallIntegerField(null=True, blank=True)

    ''' Points & standings rules '''
    points_for_win = models.SmallIntegerField(default=2)
    points_for_tie = models.SmallIntegerField(default=1)
    points_for_loss = models.SmallIntegerField(default=0)
    points_for_no_result = models.SmallIntegerField(default=1)
    points_penalty_for_forfeit = models.SmallIntegerField(default=0)
    tiebreaker_order = models.JSONField(default=list, blank=True)
    over_rate_penalty_enabled = models.BooleanField(default=False)
    over_rate_penalty_points = models.SmallIntegerField(default=0)
    

    class Meta:
        db_table = 'regulations'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(overs_per_innings__gt=0) | models.Q(match_format='TEST'),
                name='overs_per_innings_positive_unless_test'
            ),
            models.CheckConstraint(
                condition=(models.Q(match_format='TEST', overs_per_innings__isnull=True) | (~models.Q(match_format='TEST') & models.Q(overs_per_innings__gt=0))),
                name='overs_per_innings_valid_per_format'
            ),
        ]
        
    def clean(self):
        if self.match_format != MatchFormat.TEST and not self.overs_per_innings:
            raise ValidationError({'overs_per_innings': 'Required and must be > 0 for non-Test formats (including Custom).'})
        if self.overs_per_innings is not None and self.overs_per_innings <= 0:
            raise ValidationError({'overs_per_innings': 'Must be greater than 0.'})

    def __str__(self):
        return f"{self.match_format} — {self.tournament_format} (Reg #{self.regulation_id})"