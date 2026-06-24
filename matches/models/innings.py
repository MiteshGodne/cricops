from django.db import models
import uuid

class Innings(models.Model):
    innings_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='innings')
    batting_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name='innings_batted')
    fielding_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name='innings_fielded')
    innings_number = models.SmallIntegerField()
    overs_completed = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    is_super_over = models.BooleanField(default=False)
    total_score = models.SmallIntegerField(default=0)
    total_sixes = models.SmallIntegerField(default=0)
    total_fours = models.SmallIntegerField(default=0)
    total_wickets = models.SmallIntegerField(default=0)
    total_extras = models.IntegerField(default=0)
    total_wides = models.IntegerField(default=0)
    total_noballs = models.IntegerField(default=0)
    target_runs = models.SmallIntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'innings'
        verbose_name = "Innings"
        verbose_name_plural = "Innings"
        ordering = ['match', 'innings_number']
        constraints = [
            models.UniqueConstraint(fields=['match', 'innings_number'], name='unique_innings_number_per_match'),
        ]
        indexes = [models.Index(fields=['match'])]

    def __str__(self):
        return f"Innings {self.innings_number} — {self.batting_team.short_name} ({self.match_id})"