from django.contrib import admin
from .models import Match, TeamMatch, Innings, Delivery, PlayerDelivery

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'tournament', 'venue', 'status', 'start_date', 'winner_team']
    list_filter = ['status', 'tournament']
    search_fields = ['tournament__name']

@admin.register(TeamMatch)
class TeamMatchAdmin(admin.ModelAdmin):
    list_display = ['match', 'team', 'side', 'is_toss_winner', 'toss_decision']
    list_filter = ['side', 'is_toss_winner']
    search_fields = ['team__team_name']
    
@admin.register(Innings)
class InningsAdmin(admin.ModelAdmin):
    list_display = ['match', 'innings_number', 'batting_team', 'fielding_team', 'total_score', 'total_wickets', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['batting_team__team_name', 'fielding_team__team_name']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['innings', 'over_number', 'ball_number', 'runs_scored', 'extra_type', 'is_wicket', 'wicket_type']
    list_filter = ['is_wicket', 'extra_type', 'wicket_type']


@admin.register(PlayerDelivery)
class PlayerDeliveryAdmin(admin.ModelAdmin):
    list_display = ['player', 'delivery', 'performance_role', 'runs_attributed']
    list_filter = ['performance_role']
    search_fields = ['player__full_name']
