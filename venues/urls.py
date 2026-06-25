from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import VenueViewSet

router = DefaultRouter()
router.register('', VenueViewSet, basename='venue')
urlpatterns = [path('', include(router.urls))]