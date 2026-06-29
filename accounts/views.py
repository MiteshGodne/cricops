from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import User
from rest_framework import generics
from .serializers import UserSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'], url_path='approve-organizer', permission_classes=[permissions.IsAdminUser])
    def approve_organizer(self, request, pk=None):
        user = self.get_object()
        if user.apply_for != 'ORGANIZER' or user.role != 'PENDING':
            return Response({'error': 'User did not apply for ORGANIZER or is not pending.'}, status=400)
        user.role = 'ORGANIZER'
        user.save(update_fields=['role'])
        return Response({'approved': str(user.user_id), 'role': user.role})

    @action(detail=True, methods=['post'], url_path='reject', permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        user = self.get_object()
        if user.role != 'PENDING':
            return Response({'error': 'Only PENDING users can be rejected.'}, status=400)
        user.role = 'REJECTED'
        user.save(update_fields=['role'])
        return Response({'rejected': str(user.user_id)})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)