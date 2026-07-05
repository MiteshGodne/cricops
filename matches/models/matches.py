from django.db import models
import uuid

class MatchStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    LIVE = 'LIVE', 'Live'
    COMPLETED = 'COMPLETED', 'Completed'
    ABANDONED = 'ABANDONED', 'Abandoned'
class RoundType(models.TextChoices):
    LEAGUE = 'LEAGUE', 'League'
    QUALIFIER = 'QUALIFIER', 'Qualifier'
    QUARTERFINAL = 'QUARTERFINAL', 'Quarterfinal'
    SEMIFINAL = 'SEMIFINAL', 'Semifinal'
    FINAL = 'FINAL', 'Final'
class MatchResultType(models.TextChoices):
    WIN = 'WIN', 'Win'
    TIE = 'TIE', 'Tie'
    NO_RESULT = 'NO_RESULT', 'No Result'
    ABANDONED = 'ABANDONED', 'Abandoned'

class Match(models.Model):
    match_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='matches')
    venue = models.ForeignKey('venues.Venue', on_delete=models.SET_NULL, null=True, related_name='matches')
    result_type = models.CharField(max_length=20, choices=MatchResultType.choices, null=True, blank=True)
    winner_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    runnerup_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True,related_name='tournaments_runner_up')    
    group = models.ForeignKey('tournaments.Group', null=True, blank=True, on_delete=models.SET_NULL, related_name='matches')
    primary_umpire = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='umpired_matches')
    round_type = models.CharField(max_length=20, choices=RoundType.choices, default=RoundType.LEAGUE)
    round_number = models.SmallIntegerField(default=1) 
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    innings_count = models.SmallIntegerField(default=2)
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.SCHEDULED)
    result_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    standings_applied = models.BooleanField(default=False)
    is_paused = models.BooleanField(default=False)
    pause_reason = models.CharField(max_length=100, blank=True)


    class Meta:
        db_table = 'matches'
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['tournament', 'status']),
            models.Index(fields=['tournament', 'round_type']),
        ]
    def __str__(self):
        return f"{self.round_type} R{self.round_number} — {self.tournament.name}"


class TossDecision(models.TextChoices):
    BAT = 'BAT', 'Bat'
    BOWL = 'BOWL', 'Bowl'
class TeamMatchSide(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
    
class TeamMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='team_matches')
    team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name='team_matches')
    side = models.CharField(max_length=10, choices=TeamMatchSide.choices)
    is_toss_winner = models.BooleanField(default=False)
    toss_decision = models.CharField(max_length=10, choices=TossDecision.choices, blank=True)
    
    class Meta:
        db_table = 'team_matches'
        verbose_name = "Team match"
        verbose_name_plural = "Team matches"
        constraints = [
            models.UniqueConstraint(fields=['match', 'team'], name='unique_team_per_match'),
            models.UniqueConstraint(fields=['match', 'side'], name='unique_side_per_match'),
        ]
    def __str__(self):
        return f"{self.team.short_name} ({self.side}) — Match {self.match_id}"
    
        
class MatchLiveState(models.Model):
    match = models.OneToOneField(
        'matches.Match',
        on_delete=models.CASCADE,
        related_name='live_state'
    )
    current_innings = models.ForeignKey(
        'matches.Innings',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+'
    )
    current_striker = models.ForeignKey(
        'players.Player',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='live_striking'
    )
    current_non_striker = models.ForeignKey(
        'players.Player',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='live_non_striking'
    )
    current_bowler = models.ForeignKey(
        'players.Player',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='live_bowling'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_live_states'

    def __str__(self):
        return f"Live: {self.match}"