from django.contrib import admin
from .models import Team, TournamentSquad

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'short_name', 'team_head', 'coach_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['team_name', 'short_name', 'team_head__email']
    ordering = ['-created_at']
    readonly_fields = ['team_id', 'created_at', 'updated_at']

@admin.register(TournamentSquad)
class TournamentSquadAdmin(admin.ModelAdmin):
    list_display = ['player', 'team', 'tournament', 'jersey_number', 'squad_role', 'is_wicketkeeper', 'is_playing_xi']
    list_filter = ['squad_role', 'is_wicketkeeper', 'is_playing_xi']
    search_fields = ['player__full_name', 'team__team_name']