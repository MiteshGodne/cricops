from rest_framework import viewsets
from .models import Regulation, Tournament, Application
from .serializers import RegulationSerializer, TournamentSerializer, ApplicationSerializer

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('regulation', 'created_by').all()
    serializer_class = TournamentSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('team', 'tournament').all()
    serializer_class = ApplicationSerializer