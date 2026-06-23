from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'player_role', 'current_team', 'is_active']
    list_filter = ['player_role', 'is_active']
    search_fields = ['full_name']