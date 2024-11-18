from django.urls import path
from . import views

urlpatterns = [
    path('/', views.course_create_view, 'course-create'),
    path('/list/', views.course_list_view, 'course-list'),
    path('<int:pk>/update/', views.course_update_view, 'course-update'),
    path('<int:pk>/delete/', views.course_delete_view, 'course-delete'),
    path('<int:pk>/', views.course_detail_view, 'course-detail'),
    path('enrollment/', views.enrollment_create_view, 'enrollment-create'),
    path('enrollment/<int:pk>/delete/', views.enrollment_delete_view, 'enrollment-delete'),
    path('enrollment/<int:pk>/', views.enrollment_detail_view, 'enrollment-detail'),
]
