from django.contrib import admin
from .models import Regulation, Tournament, TournamentOrganizer

@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ['regulation_id', 'tournament_format','match_format', 'innings_per_match', 'overs_per_innings',  'points_for_win']
    list_filter = ['tournament_format', 'match_format']
    
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'start_date', 'end_date', 'is_public', 'created_by', 'regulation']
    list_filter = ['status', 'category']
    search_fields = ['name']
    ordering = ['-created_at']
    
@admin.register(TournamentOrganizer)
class TournamentOrganizerAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user', 'institution_name', 'institution_type', 'is_primary']
    list_filter = ['institution_type', 'is_primary']
    search_fields = ['institution_name', 'user__email']
    
#For memory -> user__email means search for an organizer in user model's email field. 