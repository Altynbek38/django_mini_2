from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound

from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from .models import Course, Enrollment
from .seriializers import CourseSerializer, EnrollmentSerializer


class CourseCreateApiView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

course_create_view = CourseCreateApiView.as_view()


class CourseListApiView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

course_list_view = CourseListApiView.as_view()


class CourseDetailApiView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'

course_detail_view = CourseDetailApiView.as_view()


class CourseUpdateApiView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'
    permission_classes = [isAdminPermission | isTeacherPermission]

course_update_view = CourseUpdateApiView.as_view()


class CourseDeleteApiView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'
    permission_classes = [isAdminPermission | isTeacherPermission]

course_delete_view = CourseDeleteApiView.as_view()


class EnrollmentListCreateApiView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "Student":
            try:
                student = Student.objects.get(user=user)
                return Enrollment.objects.filter(student=student)
            except Enrollment.DoesNotExist:
                return Enrollment.objects.none()
        elif user.role == "Teacher":
            return Enrollment.objects.filter(course__instructor=user)
        else:
            return Enrollment.objects.all()
        
    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ['Admin', 'Teacher']:
            raise PermissionDenied("You do not have permission to create enrollment.")
        
        serializer.save()

enrollment_create_view = EnrollmentListCreateApiView.as_view()


class EnrollmentDetailApiView(generics.RetrieveAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    lookup_field = 'pk'


    def get_object(self):
        user = self.request.user
        enrollment_id = self.kwargs.get(self.lookup_field)

        if user.role == "Student":
            try:
                student = Student.objects.get(user=user)
                return Enrollment.objects.get(id=enrollment_id, student=student)
            except Enrollment.DoesNotExist:
                raise PermissionDenied("You do not have permission to access this enrollment.")
        elif user.role == "Teacher":
            try:
                return Enrollment.objects.get(id=enrollment_id, course__instructor=user)
            except Enrollment.DoesNotExist:
                raise PermissionDenied("You do not have permission to access this enrollment.")
        else:
            try:
                return Enrollment.objects.get(id=enrollment_id)
            except Enrollment.DoesNotExist:
                return NotFound("Enrollment not found")

enrollment_detail_view = EnrollmentDetailApiView.as_view()


class EnrollmentDeleteApiView(generics.DestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

enrollment_delete_view = EnrollmentDeleteApiView.as_view()
