from django.contrib import admin
from tournaments.models import Regulation
@admin.register(Regulation)

class RegulationAdmin(admin.ModelAdmin):
    list_display = ['regulation_id', 'tournament_format','match_format', 'innings_per_match', 'overs_per_innings',  'points_for_win']
    list_filter = ['tournament_format', 'match_format']