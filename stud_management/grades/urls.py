from django.urls import path

from . import views

urlpatterns = [
    path('', views.grade_create_view, name='grade-create'),
    path('list/', views.grade_list_view, name='grade-list'),
    path('<int:pk>/', views.grade_update_view, name='grade-update'),
    path('<int:pk>/', views.grade_delete_view, name='grade-delete'),
]
