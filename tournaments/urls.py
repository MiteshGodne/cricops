from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RegulationViewSet, TournamentViewSet, ApplicationViewSet

router = DefaultRouter()
router.register('regulations', RegulationViewSet, basename='regulation')
router.register('tournaments', TournamentViewSet, basename='tournament')
router.register('applications', ApplicationViewSet, basename='application')
urlpatterns = [path('', include(router.urls))]