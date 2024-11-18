from rest_framework import generics

from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from .models import Grade
from .serializers import GradeSerializer

class GradeCreateApiView(generics.CreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

grade_create_view = GradeCreateApiView.as_view()


class GradeListApiView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "Student":
            try:
                student = Student.objects.get(user=user)
                return Grade.objects.filter(student=student)
            except Student.DoesNotExist:
                return Grade.objects.none()
        elif user.role == "Teacher":
            return Grade.objects.filter(teacher=user)
        return Grade.objects.all()

grade_list_view = GradeListApiView.as_view()


class GradeUpdateApiView(generics.UpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]
    lookup_field = 'pk'

grade_update_view = GradeUpdateApiView.as_view()


class GradeDestroyApiView(generics.DestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]
    lookup_field = 'pk'

grade_delete_view = GradeDestroyApiView.as_view()
