from django.urls import path
from .views import UserRoleAssignView, UserLogoutApiView

urlpatterns = [
    path('role/', UserRoleAssignView.as_view(), name='user-role'),
    path('logout/', UserLogoutApiView.as_view(), name='user-logout'),
]