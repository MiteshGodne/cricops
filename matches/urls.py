from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatchViewSet, InningsViewSet, submit_delivery, live_score

router = DefaultRouter()
router.register('matches', MatchViewSet, basename='match')
router.register('innings', InningsViewSet, basename='innings')

urlpatterns = [
    path('', include(router.urls)),
    path('matches/<uuid:match_id>/live-score/', live_score, name='live-score'),
    path('deliveries/submit/', submit_delivery, name='submit-delivery'),
]