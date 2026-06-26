from rest_framework import viewsets
from .models import Regulation, Tournament, Application, Group, TournamentStanding, TournamentOrganizer
from .serializers import RegulationSerializer, TournamentSerializer, ApplicationSerializer, GroupSerializer, TournamentStandingSerializer, TournamentOrganizerSerializer

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('regulation', 'created_by').all()
    serializer_class = TournamentSerializer

class TournamentOrganizerViewSet(viewsets.ModelViewSet):
    queryset = TournamentOrganizer.objects.select_related('tournament', 'user').all()
    serializer_class = TournamentOrganizerSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('team', 'tournament').all()
    serializer_class = ApplicationSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('tournament').all()
    serializer_class = GroupSerializer

class TournamentStandingViewSet(viewsets.ModelViewSet):
    queryset = TournamentStanding.objects.select_related('tournament', 'team', 'group').all()
    serializer_class = TournamentStandingSerializer