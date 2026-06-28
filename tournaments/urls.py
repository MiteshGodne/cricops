from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RegulationViewSet, TournamentViewSet, ApplicationViewSet, GroupViewSet, TournamentStandingViewSet, TournamentOrganizerViewSet

router = DefaultRouter()
router.register('regulations', RegulationViewSet, basename='regulation')
router.register('applications', ApplicationViewSet, basename='application')
router.register('organizers', TournamentOrganizerViewSet, basename='organizer')
router.register('groups', GroupViewSet, basename='groups')
router.register('standings', TournamentStandingViewSet, basename='standing')
router.register('tournaments', TournamentViewSet, basename='tournament')

urlpatterns = [
    path('', include(router.urls))
]