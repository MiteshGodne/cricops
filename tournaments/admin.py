from django.contrib import admin
from .models import Regulation, Tournament, TournamentOrganizer, Application, TournamentStanding, Group

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
    list_select_related = ['created_by', 'regulation']
    
@admin.register(TournamentOrganizer)
class TournamentOrganizerAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user', 'institution_name', 'institution_type', 'is_primary']
    list_filter = ['institution_type', 'is_primary']
    search_fields = ['institution_name', 'user__email']
    list_select_related = ['tournament', 'user']
#For memory -> user__email means search for an organizer in user model's email field. 

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['team', 'tournament', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['team__team_name', 'tournament__name']
    ordering = ['-created_at']
    list_select_related = ['team', 'tournament']
    
    
@admin.register(TournamentStanding)
class TournamentStandingAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'team', 'points', 'matches_played', 'net_run_rate', 'group']
    list_filter = ['tournament']
    search_fields = ['team__team_name']
    ordering = ['tournament', '-points', '-net_run_rate']
    list_select_related = ['tournament', 'team', 'group']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament']
    list_filter = ['name']
    search_fields = ['name', 'tournament__name']
    ordering = ['tournament__name', 'name']
    list_select_related = ['tournament']