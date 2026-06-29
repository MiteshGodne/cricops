from django.contrib import admin
from venues.models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'country', 'created_by']
    search_fields = ['name', 'city', 'created_by']
    list_filter = ['state', 'country']