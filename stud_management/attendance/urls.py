from django.urls import path

from . import views

urlpatterns = [
    path('', views.attendance_list_create_view, name='attendance-create-list'),
    path('mark/', views.attendance_mark_view, name='attendance-mark')
]

