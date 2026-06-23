from django.db import models
import uuid

class MatchStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    LIVE = 'LIVE', 'Live'
    COMPLETED = 'COMPLETED', 'Completed'
    ABANDONED = 'ABANDONED', 'Abandoned'

class TossDecision(models.TextChoices):
    BAT = 'BAT', 'Bat'
    BOWL = 'BOWL', 'Bowl'

class TeamMatchSide(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'

class Match(models.Model):
    match_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='matches')
    venue = models.ForeignKey('venues.Venue', on_delete=models.SET_NULL, null=True, related_name='matches')
    winner_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    runnerup_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_lost')
    primary_umpire = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='umpired_matches')
    start_date = models.DateTimeField()
    innings_count = models.SmallIntegerField(default=2)
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.SCHEDULED)
    result_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        ordering = ['start_date']
        indexes = [models.Index(fields=['tournament', 'status'])]

    def __str__(self):
        return f"Match {self.match_id} — {self.tournament.name}"

class TeamMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='team_matches')
    team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name='team_matches')
    side = models.CharField(max_length=10, choices=TeamMatchSide.choices)
    is_toss_winner = models.BooleanField(default=False)
    toss_decision = models.CharField(max_length=10, choices=TossDecision.choices, blank=True)

    class Meta:
        db_table = 'team_matches'
        constraints = [
            models.UniqueConstraint(fields=['match', 'team'], name='unique_team_per_match'),
            models.UniqueConstraint(fields=['match', 'side'], name='unique_side_per_match'),
        ]

    def __str__(self):
        return f"{self.team.short_name} ({self.side}) — Match {self.match_id}"