from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TeamViewSet, TeamMatchViewSet, TournamentSquadViewSet

router = DefaultRouter()
router.register('teams', TeamViewSet, basename='team')
router.register('team-matches', TeamMatchViewSet, basename='team-match')
router.register('squads', TournamentSquadViewSet, basename='squad')
urlpatterns = [path('', include(router.urls))]