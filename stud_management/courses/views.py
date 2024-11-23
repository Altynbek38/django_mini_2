from rest_framework import generics, pagination
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from django_filters.rest_framework import DjangoFilterBackend   
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
import redis

from analytics.models import CourseViewLog
from users.permissions import isAdminPermission, isTeacherPermission
from students.models import Student
from .models import Course, Enrollment
from .seriializers import CourseSerializer, EnrollmentSerializer

logger = logging.getLogger(__name__)
redis_instance = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)

class CourseCreateApiView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

    @swagger_auto_schema(
        operation_description="Create a new course.",
        request_body=CourseSerializer,
        responses={201: openapi.Response(description="Course created", schema=CourseSerializer)}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

course_create_view = CourseCreateApiView.as_view()


class CourseListApiView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'description']

    @swagger_auto_schema(
        operation_description="Retrieve a list of courses with optional filtering by name or description.",
        responses={200: CourseSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        cache_key = f"courses:list:{str(self.request.GET.urlencode)}"

        cached_queryset = cache.get(cache_key)
        if cached_queryset:
            return cached_queryset
        
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)

        cache.set(cache_key, queryset, timeout=3600)
        return queryset

course_list_view = CourseListApiView.as_view()


class CourseDetailApiView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="Retrieve a detail of the course.",
        responses={200: CourseSerializer},
    )
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user.is_authenticated:
            CourseViewLog.objects.create(user=request.user, course=course)
        return super().get(request, *args, **kwargs)

course_detail_view = CourseDetailApiView.as_view()


class CourseUpdateApiView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'
    permission_classes = [isAdminPermission | isTeacherPermission]

    @swagger_auto_schema(
        operation_description="Update the courses.",
        responses={200: CourseSerializer},
        request_body=CourseSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

course_update_view = CourseUpdateApiView.as_view()


class CourseDeleteApiView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'pk'
    permission_classes = [isAdminPermission | isTeacherPermission]

    @swagger_auto_schema(
        operation_description="Delete the courses.",
        responses={204: CourseSerializer},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


course_delete_view = CourseDeleteApiView.as_view()


class EnrollmentListCreateApiView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    @swagger_auto_schema(
        operation_description="Create an enrollment for a student in a course.",
        request_body=EnrollmentSerializer,
        responses={201: openapi.Response(description="Enrollment created", schema=EnrollmentSerializer)},
        security=[{'JWT Authentication': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        logger.info(f"Fetching enrollments for user: {user.username}, role: {user.role}")

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
        instance = serializer.save()
        logger.info(f"New enrollment created: {instance}")
        
def perform_create(self, serializer):
    user = self.request.user

    if user.role not in ['Admin', 'Teacher']:
        raise PermissionDenied("You do not have permission to create enrollment.")
    
    student = serializer.validated_data.get('student')
    course = serializer.validated_data.get('course')

    if not Student.objects.filter(id=student.id).exists():
        raise ValidationError("The student does not exist.")
    if not Course.objects.filter(id=course.id).exists():
        raise ValidationError("The course does not exist.")

    serializer.save()

enrollment_create_view = EnrollmentListCreateApiView.as_view()


class EnrollmentDetailApiView(generics.RetrieveAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="Retrieve a detail of the enrollment.",
        responses={200: EnrollmentSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_description="Delete the enrollment.",
        responses={204: EnrollmentSerializer}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

enrollment_delete_view = EnrollmentDeleteApiView.as_view()
