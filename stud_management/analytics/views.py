from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import ApiRequestLog, CourseViewLog
from users.models import User
from courses.models import Course

class APIUsageMetricsView(APIView):
    def get(self, request):
        data = {
            "total_requests": ApiRequestLog.objects.count(),
            "requests_per_user": ApiRequestLog.objects.values('user__username').annotate(count=Count('id')).order_by('-count'),
            "most_active_users": ApiRequestLog.objects.values('user__username').annotate(count=Count('id')).order_by('-count')[:5],
        }
        return Response(data)

class CoursePopularityMetricsView(APIView):
    def get(self, request):
        data = {
            "most_viewed_courses": CourseViewLog.objects.values('course__name').annotate(count=Count('id')).order_by('-count')[:5],
        }
        return Response(data)