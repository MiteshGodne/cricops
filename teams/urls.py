from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TeamViewSet, TournamentSquadViewSet

router = DefaultRouter()
router.register('squads', TournamentSquadViewSet, basename='squad')
router.register('teams', TeamViewSet, basename='team')
urlpatterns = [
    path('', include(router.urls))
]