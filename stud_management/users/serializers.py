from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User

class CustomUserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        ref_name = 'CustomUserCreateSerializer'


class CustomUserSerializer(BaseUserSerializer):
    
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        ref_name = 'CustomUserSerializer'


