from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.student_list_view, name='student-list'),
    path('<int:pk>/update/', views.student_update_view, name='student-update'),
    path('<int:pk>/delete/', views.student_delete_view, name='student-delete'),
    path('<int:pk>/', views.student_detail_view, name='student-detail'),
]
