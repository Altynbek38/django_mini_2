from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound

from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceListCreateApiView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

attendance_list_create_view = AttendanceListCreateApiView.as_view()


class AttendanceaMarkApiView(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    lookup_field = 'pk'


    def perform_update(self, serializer):
        user = self.request.user

        if user.role != "Student":
            raise PermissionDenied("Only students can mark their attendance.")

        try:
            student = Student.objects.get(user=user)
            attendance_record = Attendance.objects.get(student=student, course=serializer.validated_data['course'])
            attendance_record.status = 'present'
            attendance_record.save()
        except Attendance.DoesNotExist:
            serializer.save(student=student, status='present')
        except Student.DoesNotExist:
            raise NotFound("Student not found.")

attendance_mark_view = AttendanceaMarkApiView.as_view()
