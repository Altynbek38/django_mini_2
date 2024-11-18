from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import isAdminPermission
from .models import User

class UserRoleAssignView(APIView):
    permission_classes = [isAdminPermission]


    def post(self, request):
        user_id = request.data.get('user_id')
        role = request.data.get('role')

        try:
            user = User.objects.get(id=user_id)
            user.role = role
            user.save()
            return Response({'message': 'Role assigned successfully!'}, status=200)
        except:
            Response({'error': 'User not found'}, status=404)
