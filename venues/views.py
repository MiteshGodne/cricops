from rest_framework import viewsets
from .models import Venue
from .serializers import VenueSerializer
from core.permissions import ReadOnly, IsOrganizer

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

