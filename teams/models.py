import uuid
from django.db import models

class Team(models.Model):
    team_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    team_head = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='teams_headed')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_teams')
    
    team_name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=10, unique=True) 
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