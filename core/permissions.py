from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
    
class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ORGANIZER')
    
class IsTeamHead(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'TEAMHEAD')

class IsOrganizerOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ORGANIZER')
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'tournament'):
            return obj.tournament.created_by == request.user
        return False
    
class IsTeamHeadOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'TEAMHEAD')
    def has_object_permission(self, request, view, obj):
        return obj.team_head == request.user
    
class IsMatchOrganizerOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ORGANIZER'
    def has_object_permission(self, request, view, obj):
        return obj.tournament.created_by == request.user
    
class IsCreatorOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated 
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class IsOwnTeamHead(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.team.team_head == request.user or obj.team.created_by == request.user
    
class IsUmpireForMatch(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role != 'UMPIRE':
            return False
        innings_id = request.data.get('innings_id')
        if not innings_id:
            return False
        try:
            from matches.models import Innings
            innings = Innings.objects.select_related('match').get(innings_id=innings_id)
            return innings.match.primary_umpire == request.user
        except Innings.DoesNotExist:
            return False
    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'UMPIRE' and obj.primary_umpire == request.user)

class IsUmpireForMatchFromURL(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role != 'UMPIRE':
            return False
        match_id = request.data.get('match_id')
        if not match_id:
            return False
        from matches.models import Match
        try:
            match = Match.objects.get(match_id=match_id)
            return match.primary_umpire == request.user
        except Match.DoesNotExist:
            return False
        
class IsPlayerTeamHeadOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TEAMHEAD'
    def has_object_permission(self, request, view, obj):
        if obj.current_team is None:
            return False
        return obj.current_team.team_head == request.user

class IsGroupTournamentOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ORGANIZER'
    def has_object_permission(self, request, view, obj):
        if obj.tournament is None:
            return False
        return obj.tournament.created_by == request.user
    
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
    
class IsTournamentOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ORGANIZER'
    
    def has_object_permission(self, request, view, obj):
        from tournaments.models import TournamentOrganizer, Tournament
        tournament = None
        if isinstance(obj, Tournament):
            tournament = obj
        elif hasattr(obj, 'tournament'):
            tournament = obj.tournament
        if not tournament:
            return False
        return TournamentOrganizer.objects.filter(tournament=tournament, user=request.user).exists()