from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly

class IsOrganizer(BasePermission):
    # Grants access only to ORGANIZER
    def has_permission(self, request, view, obj):
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'tournament'):
            return obj.tournament.created_by == request.user
        return False

class IsOrganizerOwner(BasePermission):
    # Only organizer's own tournaments can be modified
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class IsTeamHead(BasePermission):
    # Grants access only to TEAMHEAD
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'TEAMHEAD')
    
class IsTeamHeadOwner(BasePermission):
    # Only teamhead's own team can be modified 
    def has_object_permission(self, request, view, obj):
        return obj.team_head == request.user or obj.created_by == request.user

class IsAssignedUmpire(BasePermission):
    # Umpire can only submit deliveries for their assigned match
    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'UMPIRE' and obj.primary_umpire == request.user)
        
class IsOwnTeamHead(BasePermission):
    # Prevents a teamhead from modifying another team's squad
    def has_object_permission(self, request, view, obj):
        return obj.team.team_head == request.user or obj.team.created_by == request.user

class IsPendingUmpire(BasePermission):
    # Used in assign_umpire to verify target user applied as umpire
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ORGANIZER'
    
class IsUmpireForMatch(BasePermission):
    # Grants permission for delivery update to the innings' match's primary_umpire
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role != 'UMPIRE':
            return False
        innings_id = request.data.get('innings_id')
        if not innings_id:
            return False
        from matches.models import Innings
        try:
            innings = Innings.objects.select_related('match').get(innings_id=innings_id)
            return innings.match.primary_umpire == request.user
        except Innings.DoesNotExist:
            return False

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')