from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create your views here.

class RegisterViewSet(UserViewSet):
    pass

class LoginViewSet(TokenObtainPairView):
    pass

class RefreshViewSet(TokenRefreshView):
    pass