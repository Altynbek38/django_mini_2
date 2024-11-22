from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from notifications.tasks import send_attendance_reminder
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceCreateSerializer

logger = logging.getLogger(__name__)

class AttendanceListCreateApiView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceCreateSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

    @swagger_auto_schema(
        operation_description="Open a new Attendance.",
        request_body=AttendanceCreateSerializer,
        responses={201: openapi.Response(description="Attendance opened", schema=AttendanceCreateSerializer)}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()

        send_attendance_reminder.delay(instance.student.name, instance.student.email)
        return instance

attendance_list_create_view = AttendanceListCreateApiView.as_view()


class AttendanceaMarkApiView(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="Update the courses.",
        responses={200: AttendanceSerializer},
        request_body=AttendanceSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


    def perform_update(self, serializer):
        user = self.request.user
        logger.info({})

        if user.role != "Student":
            logger.error(f"Attendance marking failed: Only students can mark their attendance.")
            raise PermissionDenied("Only students can mark their attendance.")

        try:
            student = Student.objects.get(user=user)
            attendance_record = Attendance.objects.get(student=student, course=serializer.validated_data['course'])
            attendance_record.status = 'present'
            attendance_record.save()
            logger.info(f"Attendance marked: {student.user.username} for course {attendance_record.course.name} on {attendance_record.date}.")
        except Attendance.DoesNotExist:
            logger.error(f"Attendance marking failed: Attendance is not open.")
            serializer.save(student=student, status='present')
        except Student.DoesNotExist:
            logger.error(f"Attendance marking failed: Student with ID {student.id} does not exist.")
            raise NotFound("Student not found.")

attendance_mark_view = AttendanceaMarkApiView.as_view()
