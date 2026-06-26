from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatchViewSet, InningsViewSet, TeamMatchViewSet, DeliveryViewSet, PlayerDeliveryViewSet, submit_delivery, live_score

router = DefaultRouter()
router.register('', MatchViewSet, basename='match')
router.register('innings', InningsViewSet, basename='innings')
router.register('team-matches', TeamMatchViewSet, basename='team-match')
router.register('deliveries-list', DeliveryViewSet, basename='delivery')
router.register('player-deliveries', PlayerDeliveryViewSet, basename='player-delivery')

urlpatterns = [
    path('', include(router.urls)),
    path('matches/<uuid:match_id>/live-score/', live_score, name='live-score'),
    path('deliveries/submit/', submit_delivery, name='submit-delivery'),
]