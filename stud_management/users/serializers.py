from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = User.objects.get(pk=self.user.id)
        serializer = UserSerializer(user)
        data.update({'user': serializer.data})
        return data

