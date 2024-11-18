from rest_framework import serializers

from .models import Course, Enrollment

class CourseSerializer(serializers.Serializer):
    class Meta:
        model = Course
        fields = '__all__'
        
class EnrollmentSerializer(serializers.Serializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
