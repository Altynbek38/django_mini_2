from django.urls import path
from .views import UserRoleAssignView

urlpatterns = [
    path('role/', UserRoleAssignView.as_view(), 'user-role'),
]
