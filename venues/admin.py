from django.contrib import admin
from venues.models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'country']
    search_fields = ['name', 'city']
    list_filter = ['state', 'country']