import uuid
from django.db import models

class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
    WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

class Application(models.Model):
    application_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name='tournament_applications')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.PROTECT, related_name='team_applications')
    registered_name = models.CharField(max_length=255)
    registered_short_name = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True) 
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_applications'
    )
    
    class Meta:
        db_table = 'applications'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'tournament'],
                name='unique_team_tournament_application'
            ),
            models.UniqueConstraint(
                fields=['tournament', 'registered_name'], 
                name='unique_team_name_per_tournament'
            ),
            models.UniqueConstraint(
                fields=['tournament', 'registered_short_name'], 
                name='unique_short_name_per_tournament'
            )
        ]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['tournament', 'status']),
        ]

    def __str__(self):
        return f"{self.team.team_name} → {self.tournament.name} ({self.status})"