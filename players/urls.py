from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PlayerViewSet

router = DefaultRouter()
router.register('', PlayerViewSet, basename='player')
urlpatterns = [
    path('', include(router.urls))
]