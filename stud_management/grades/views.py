from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from notifications.tasks import notify_grade_update
from .models import Grade
from .serializers import GradeSerializer

class GradeCreateApiView(generics.CreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

    @swagger_auto_schema(
        operation_description="Create a new grade.",
        request_body=GradeSerializer,
        responses={201: openapi.Response(description="Grade created", schema=GradeSerializer)}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

grade_create_view = GradeCreateApiView.as_view()


class GradeListApiView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of grade with optional filtering.",
        responses={200: GradeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_description="Update the courses.",
        responses={200: GradeSerializer},
        request_body=GradeSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()

        notify_grade_update.delay(instance.student.id, instance.course.name, instance.grade)
        return instance


grade_update_view = GradeUpdateApiView.as_view()


class GradeDestroyApiView(generics.DestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="Delete the courses.",
        responses={204: GradeSerializer},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

grade_delete_view = GradeDestroyApiView.as_view()
