import uuid
from django.db import models

class TournamentStanding(models.Model):
    standing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='standings')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='tournament_standings')
    matches_played = models.SmallIntegerField(default=0)
    matches_won = models.SmallIntegerField(default=0)
    matches_lost = models.SmallIntegerField(default=0)
    matches_tied = models.SmallIntegerField(default=0)
    matches_no_result = models.SmallIntegerField(default=0)
    points = models.SmallIntegerField(default=0)
    net_run_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tournament_standings'
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'team'],
                name='unique_tournament_team_standing'
            )
        ]
        ordering = ['-points', '-net_run_rate']
        indexes = [
            models.Index(fields=['tournament', '-points']),
        ]

    def __str__(self):
        return f"{self.tournament.name} - {self.team.team_name}: {self.points} pts"