from django.db import models
import uuid

class PlayerRole(models.TextChoices):
    BATSMAN = 'BATSMAN', 'Batsman'
    BOWLER = 'BOWLER', 'Bowler'
    ALL_ROUNDER = 'ALL_ROUNDER', 'All Rounder'
    WICKETKEEPER = 'WICKETKEEPER', 'Wicketkeeper'

class Player(models.Model):
    player_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    current_team = models.ForeignKey(
        'teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='roster'
    )
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    player_role = models.CharField(max_length=20, choices=PlayerRole.choices)
    nationality = models.CharField(max_length=100, blank=True)
    identity_document = models.FileField(upload_to='player_documents/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'players'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['current_team']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if self.full_name:
            self.full_name = ' '.join(w.capitalize() for w in self.full_name.strip().split())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.player_role})"