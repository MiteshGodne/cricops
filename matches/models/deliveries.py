from django.db import models
import uuid

class ExtraType(models.TextChoices):
    WIDE = 'WIDE', 'Wide'
    NO_BALL = 'NO_BALL', 'No Ball'
    BYE = 'BYE', 'Bye'
    LEG_BYE = 'LEG_BYE', 'Leg Bye'
    NONE = 'NONE', 'None'

class WicketType(models.TextChoices):
    BOWLED = 'BOWLED', 'Bowled'
    CAUGHT = 'CAUGHT', 'Caught'
    LBW = 'LBW', 'LBW'
    RUN_OUT = 'RUN_OUT', 'Run Out'
    STUMPED = 'STUMPED', 'Stumped'
    HIT_WICKET = 'HIT_WICKET', 'Hit Wicket'
    NONE = 'NONE', 'None'

class Delivery(models.Model):
    delivery_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='deliveries')
    innings = models.ForeignKey('matches.Innings', on_delete=models.CASCADE, related_name='deliveries')
    ball_sequence = models.IntegerField()
    over_number = models.SmallIntegerField()
    ball_number = models.SmallIntegerField()
    runs_scored = models.SmallIntegerField(default=0)
    extra_runs = models.SmallIntegerField(default=0)
    extra_type = models.CharField(max_length=10, choices=ExtraType.choices, default=ExtraType.NONE)
    is_legal_delivery = models.BooleanField(default=True)
    is_wicket = models.BooleanField(default=False)
    wicket_type = models.CharField(max_length=20, choices=WicketType.choices, default=WicketType.NONE)

    class Meta:
        db_table = 'deliveries'
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = ['innings', 'ball_sequence']
        constraints = [
            models.UniqueConstraint(fields=['innings', 'ball_sequence'], name='unique_ball_sequence_per_innings'),
        ]
        indexes = [models.Index(fields=['match']), models.Index(fields=['innings'])]

    def __str__(self):
        return f"Over {self.over_number}.{self.ball_number} — Innings {self.innings_id}"


class DeliveryPerformanceRole(models.TextChoices):
    STRIKER = 'STRIKER', 'Striker'
    NON_STRIKER = 'NON_STRIKER', 'Non Striker'
    BOWLER = 'BOWLER', 'Bowler'
    FIELDER_CATCH = 'FIELDER_CATCH', 'Fielder Catch'
    FIELDER_RUNOUT = 'FIELDER_RUNOUT', 'Fielder Runout'

class PlayerDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='delivery_performances')
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='player_deliveries')
    performance_role = models.CharField(max_length=20, choices=DeliveryPerformanceRole.choices)
    runs_attributed = models.SmallIntegerField(default=0)
    dismissal_info = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'player_deliveries'
        verbose_name = "Player delivery"
        verbose_name_plural = "Player deliveries"
        
        constraints = [
            models.UniqueConstraint(fields=['delivery', 'player', 'performance_role'], name='unique_player_role_per_delivery'),
        ]
        indexes = [models.Index(fields=['player']), models.Index(fields=['delivery'])]

    def __str__(self):
        return f"{self.player.full_name} — {self.performance_role} ({self.delivery_id})"