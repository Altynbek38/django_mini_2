from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_create_view, name='course-create'),
    path('list/', views.course_list_view, name='course-list'),
    path('<int:pk>/update/', views.course_update_view, name='course-update'),
    path('<int:pk>/delete/', views.course_delete_view, name='course-delete'),
    path('<int:pk>/', views.course_detail_view, name='course-detail'),
    path('enrollment/', views.enrollment_create_view, name='enrollment-create'),
    path('enrollment/<int:pk>/delete/', views.enrollment_delete_view, name='enrollment-delete'),
    path('enrollment/<int:pk>/', views.enrollment_detail_view, name='enrollment-detail'),
]
