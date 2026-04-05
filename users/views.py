from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    RegisterSerializer, UserSerializer,
    UpdateRoleSerializer, UpdateStatusSerializer,
)
from .permissions import IsAdmin, IsActiveUser


class RegisterView(generics.CreateAPIView):
    # POST /api/auth/register/

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': 'User registered successfully.', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
   
    # POST /api/auth/login/
    # Returns access + refresh JWT tokens. 
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    
    # GET  /api/auth/me/   — checke profile dekho
    # PUT  /api/auth/me/   — update Name 
   
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    # GET /api/users/
    # Admin only: all users list.
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all().order_by('-created_at')


class UpdateUserRoleView(APIView):
    # PATCH /api/users/<id>/role/
    # Admin only:  Update role of a specific user
    
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateRoleSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Role updated.', 'user': UserSerializer(user).data})


class UpdateUserStatusView(APIView):
    
    # PATCH /api/users/<id>/status/
    # Admin only: user ko active/inactive karo.
    
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateStatusSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action = 'activated' if user.is_active else 'deactivated'
        return Response({'message': f'User {action} successfully.'})