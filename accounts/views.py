from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import User
from rest_framework import generics
from .serializers import UserSerializer, RegisterSerializer
from core.permissions import IsAuthenticated, IsAdminUser, IsOrganizer, AllowAny

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('list', 'retrieve'):
            return [IsOrganizer()]
        if self.action == 'pending_umpires':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'], url_path='approve-organizer', permission_classes=[IsAdminUser])
    def approve_organizer(self, request, pk=None):
        user = self.get_object()
        if user.apply_for != 'ORGANIZER' or user.role != 'PENDING':
            return Response({'error': 'User did not apply for ORGANIZER or is not pending.'}, status=400)
        user.role = 'ORGANIZER'
        user.save(update_fields=['role'])
        return Response({'approved': str(user.user_id), 'role': user.role})

    @action(detail=True, methods=['post'], url_path='reject', permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        user = self.get_object()
        if user.role != 'PENDING':
            return Response({'error': 'Only PENDING users can be rejected.'}, status=400)
        user.role = 'REJECTED'
        user.save(update_fields=['role'])
        return Response({'rejected': str(user.user_id)})

    @action(detail=False, methods=['get'], url_path='pending-umpires', permission_classes=[IsAuthenticated])
    def pending_umpires(self, request):
        if request.user.role != 'ORGANIZER':
            return Response({'error': 'Only organizers can view pending umpires.'}, status=403)
        users = User.objects.filter(apply_for='UMPIRE', role='PENDING')
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)