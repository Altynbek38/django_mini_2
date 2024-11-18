from django.db import models

from students.models import Student
from users.models import User
from courses.models import Course

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.CharField(max_length=3)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name}-{self.course.name}: {self.grade}"
