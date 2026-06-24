import uuid
from django.db import models

class Team(models.Model):
    team_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    team_head = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='teams_headed')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_teams')
    
    team_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10) 
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)  
    coach_name = models.CharField(max_length=255, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        ordering = ['team_name']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.team_name} ({self.short_name})"
    

class SquadRole(models.TextChoices):
    PLAYER = 'PLAYER', 'Player'
    CAPTAIN = 'CAPTAIN', 'Captain'
    VICE_CAPTAIN = 'VICE_CAPTAIN', 'Vice Captain'

class TournamentSquad(models.Model):
    squad_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey('tournaments.Application', on_delete=models.CASCADE, related_name='squad_entries')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='squad_entries')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='tournament_squads')
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='squad_entries')
    jersey_number = models.PositiveSmallIntegerField()
    squad_role = models.CharField(max_length=20, choices=SquadRole.choices, default=SquadRole.PLAYER)
    is_wicketkeeper = models.BooleanField(default=False)
    is_playing_xi = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tournament_squads'
        ordering = ['team', 'jersey_number']
        indexes = [
            models.Index(fields=['tournament', 'team']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['tournament', 'player'], name='unique_player_per_tournament'),
            models.UniqueConstraint(fields=['tournament', 'team', 'jersey_number'], name='unique_jersey_per_team_per_tournament'),
        ]

    def __str__(self):
        return f"{self.player.full_name} — {self.team.short_name} ({self.tournament})"