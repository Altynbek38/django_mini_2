from rest_framework import serializers

from students.serializers import StudentSerializer
from .models import Attendance

class AttendanceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = ['student', 'course', 'status']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
