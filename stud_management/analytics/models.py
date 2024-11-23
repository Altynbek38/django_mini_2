from django.db import models
from django.utils.timezone import now

from users.models import User
from courses.models import Course

class ApiRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user} - {self.endpoint} - {self.method}"
    

class CourseViewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user} viewed {self.course} at {self.timestamp}"
