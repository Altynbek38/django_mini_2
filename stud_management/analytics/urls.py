from django.urls import path
from .views import APIUsageMetricsView, CoursePopularityMetricsView

urlpatterns = [
    path('api-usage/', APIUsageMetricsView.as_view(), name='api-usage'),
    path('course-popularity/', CoursePopularityMetricsView.as_view(), name='course-popularity'),
]
