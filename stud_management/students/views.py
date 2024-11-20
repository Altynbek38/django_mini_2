from rest_framework import generics, pagination
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import isAdminPermission, isTeacherPermission
from .models import Student
from .serializers import StudentSerializer

class StudentListApiView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    permission_classes = [isAdminPermission | isTeacherPermission]

student_list_view = StudentListApiView.as_view()


class StudentDetailApiView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

student_detail_view = StudentDetailApiView.as_view()


class StudentUpdateApiView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

student_update_view = StudentUpdateApiView.as_view()
