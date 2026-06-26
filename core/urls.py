from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "CricOps API", "endpoints": ["/api/tournaments/", "/api/matches/", "/api/teams/"]})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('api/accounts/', include('accounts.urls')),
    path('api/venues/', include('venues.urls')),
    path('api/tournaments/', include('tournaments.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/players/', include('players.urls')),
    path('api/matches/', include('matches.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)