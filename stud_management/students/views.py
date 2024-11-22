from rest_framework import generics, pagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from urllib.parse import urlencode
import redis

from users.permissions import isAdminPermission, isTeacherPermission
from .models import Student
from .serializers import StudentSerializer

redis_instance = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)

class StudentListApiView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    permission_classes = [isAdminPermission | isTeacherPermission]

    def get_queryset(self):

        cache_key = f"students:{self.request.GET.urlencode}"

        cached_queryset = cache.get(cache_key)
        if cached_queryset:
            return cached_queryset

        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)

        cache.set(cache_key, queryset, timeout=3600)        

        return queryset

student_list_view = StudentListApiView.as_view()


class StudentDetailApiView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'pk'

student_detail_view = StudentDetailApiView.as_view()


class StudentUpdateApiView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]

student_update_view = StudentUpdateApiView.as_view()

class StudentDeleteApiView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [isAdminPermission | isTeacherPermission]
    lookup_field = 'pk'

student_delete_view = StudentDeleteApiView.as_view()
