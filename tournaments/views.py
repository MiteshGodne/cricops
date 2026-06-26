from rest_framework import viewsets
from .models import Regulation, Tournament, Application, Group, TournamentStanding
from .serializers import RegulationSerializer, TournamentSerializer, ApplicationSerializer, GroupSerializer, TournamentStandingSerializer

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('regulation', 'created_by').all()
    serializer_class = TournamentSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('team', 'tournament').all()
    serializer_class = ApplicationSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('tournament').all()
    serializer_class = GroupSerializer

class TournamentStandingViewSet(viewsets.ModelViewSet):
    queryset = TournamentStanding.objects.select_related('tournament', 'team', 'group').all()
    serializer_class = TournamentStandingSerializer