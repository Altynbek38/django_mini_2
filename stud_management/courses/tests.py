from django.test import TestCase
from django.core.cache import cache
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from students.models import Student
from .models import Course, Enrollment

class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="instructor", role="Teacher")
        self.course = Course.objects.create(name="Math 101", description="Basic Math", instructor=self.user)

    def test_course_creation(self):
        self.assertEqual(self.course.name, "Math 101")
        self.assertEqual(self.course.description, "Basic Math")
        self.assertEqual(self.course.instructor, self.user)

class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="student", role="Student")
        self.student = Student.objects.create(user=self.user, name="John Doe")
        self.course = Course.objects.create(name="Math 101", instructor=self.user)
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    def test_enrollment_creation(self):
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.course, self.course)


class CourseApiTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.client.login(username="teacher", password="password")
        self.course = Course.objects.create(name="Math 101", description="Basic Math", instructor=self.teacher)
        self.course_data = {"name": "Physics 101", "description": "Basic Physics", "instructor": self.teacher.id}

    def test_course_create(self):
        response = self.client.post('/courses/', self.course_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_list(self):
        response = self.client.get('/courses/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_update(self):
        response = self.client.put(f'/courses/{self.course.id}/update/', {"name": "Advanced Math", "description": "Updated Math"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_delete(self):
        response = self.client.delete(f'/courses/{self.course.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class EnrollmentApiTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.student_user = User.objects.create_user(username="student", password="password", role="Student")
        self.student = Student.objects.create(user=self.student_user, name="John Doe")
        self.course = Course.objects.create(name="Math 101", instructor=self.teacher)
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    def test_enrollment_create(self):
        self.client.login(username="teacher", password="password")
        response = self.client.post('/enrollment/', {"student": self.student.id, "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enrollment_list(self):
        self.client.login(username="teacher", password="password")
        response = self.client.get('/enrollment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_delete(self):
        self.client.login(username="teacher", password="password")
        response = self.client.delete(f'/enrollment/{self.enrollment.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class CourseApiCacheTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.client.login(username="teacher", password="password")
        self.course = Course.objects.create(name="Math 101", description="Basic Math", instructor=self.teacher)

    def test_course_list_cache(self):

        response1 = self.client.get('/courses/list/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        Course.objects.create(name="Physics 101", description="Basic Physics", instructor=self.teacher)

        response2 = self.client.get('/courses/list/')
        self.assertEqual(len(response2.data['results']), 1) 


        cache.clear()

        response3 = self.client.get('/courses/list/')
        self.assertEqual(len(response3.data['results']), 2) 


class PermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password", role="Admin")
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.student = User.objects.create_user(username="student", password="password", role="Student")

    def test_course_create_permission(self):

        self.client.login(username="admin", password="password")
        response = self.client.post('/courses/', {"name": "Chemistry 101", "description": "Basic Chemistry", "instructor": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client.login(username="teacher", password="password")
        response = self.client.post('/courses/', {"name": "Physics 101", "description": "Basic Physics", "instructor": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client.login(username="student", password="password")
        response = self.client.post('/courses/', {"name": "Biology 101", "description": "Basic Biology", "instructor": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enrollment_permission(self):

        self.client.login(username="admin", password="password")
        response = self.client.post('/enrollment/', {"student": 1, "course": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client.login(username="teacher", password="password")
        response = self.client.post('/enrollment/', {"student": 1, "course": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client.login(username="student", password="password")
        response = self.client.post('/enrollment/', {"student": 1, "course": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
