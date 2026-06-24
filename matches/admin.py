from django.contrib import admin
from .models import Match, TeamMatch, Innings, Delivery, PlayerDelivery, MatchLiveState

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'tournament', 'venue', 'status', 'start_date', 'winner_team', 'runnerup_team', 'group']
    list_filter = ['status', 'tournament']
    search_fields = ['tournament__name' ,'venue__name']
    ordering = ['-start_date']
    list_select_related = ['tournament', 'venue', 'winner_team', 'group']   # >> to prevent n+1 query searches

@admin.register(TeamMatch)
class TeamMatchAdmin(admin.ModelAdmin):
    list_display = ['match', 'team', 'side', 'is_toss_winner', 'toss_decision']
    list_filter = ['side', 'is_toss_winner']
    search_fields = ['team__team_name']
    list_select_related = ['match', 'team']
    
@admin.register(Innings)
class InningsAdmin(admin.ModelAdmin):
    list_display = ['match', 'innings_number', 'batting_team', 'fielding_team', 'total_score', 'total_wickets', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['batting_team__team_name', 'fielding_team__team_name']
    list_select_related = ['match', 'batting_team', 'fielding_team']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['innings', 'over_number', 'ball_number', 'runs_scored', 'extra_type', 'is_wicket', 'wicket_type']
    list_filter = ['is_wicket', 'extra_type', 'wicket_type']
    search_fields = ['innings__match__tournament__name']
    list_select_related = ['innings__match']


@admin.register(PlayerDelivery)
class PlayerDeliveryAdmin(admin.ModelAdmin):
    list_display = ['player', 'delivery', 'performance_role', 'runs_attributed']
    list_filter = ['performance_role']
    search_fields = ['player__full_name', 'delivery__innings__match__tournament__name']
    list_select_related = ['player', 'delivery__innings__match']
    
    
@admin.register(MatchLiveState)
class MatchLiveStateAdmin(admin.ModelAdmin):
    list_display = ['match','current_innings','current_striker','current_non_striker', 'current_bowler', 'balls_remaining']    
    list_filter = ['match__status', 'match__tournament']
    search_fields = ['match__tournament__name', 'match__team1__team_name', 'match__team2__team_name']
    list_select_related = ['match', 'match__tournament', 'current_innings', 'current_striker', 'current_non_striker', 'current_bowler']