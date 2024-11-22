from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from students.models import Student
from .permissions import isAdminPermission
from .serializers import CustomUserSerializer
from .models import User

class UserRoleAssignView(generics.UpdateAPIView):
    permission_classes = [isAdminPermission]
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Update the courses.",
        responses={200: CustomUserSerializer},
        request_body=CustomUserSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_object(self):
        email = self.request.data.get('email')
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            raise Response({'error': 'User not found'}, status=404)

    def perform_update(self, serializer):
        user = self.get_object()
        role = self.request.data.get('role')
        
        if not role:
            raise Response({'error': 'Role is required'}, status=400)
        
        user.role = role
        user.save()

        if role == 'student':
            if not Student.objects.filter(user=user).exists():
                Student.objects.create(
                    user=user,
                    name=user.username,
                    email=user.email,
                )
        
        return Response({'message': 'Role assigned successfully!'}, status=200)


class UserLogoutApiView(APIView):
    @swagger_auto_schema(
        operation_description="Logout",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['refresh_token']),
        responses={
            205: openapi.Response(description="Logged out successfully."),
            400: openapi.Response(description="Bad Request. Invalid or missing refresh token.")
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=205)
        except Exception as e:
            return Response(status=400)