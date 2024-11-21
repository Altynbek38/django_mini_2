from django.test import TestCase
from django.core.cache import cache
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from .models import Student



class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", role="Student")
        self.student = Student.objects.create(
            user=self.user, name="John Doe", email="john@example.com", dob="2000-01-01"
        )

    def test_student_creation(self):
        self.assertEqual(self.student.name, "John Doe")
        self.assertEqual(self.student.email, "john@example.com")
        self.assertEqual(self.student.user, self.user)

    def test_student_str_representation(self):
        self.assertEqual(str(self.student), "John Doe")


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class StudentListApiViewTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password", role="Admin")
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.student_user = User.objects.create_user(username="student", password="password", role="Student")
        Student.objects.create(user=self.student_user, name="John Doe", email="john@example.com")
        self.client.login(username="admin", password="password")

    def test_student_list(self):
        response = self.client.get('/students/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_student_list_cache(self):
        response1 = self.client.get('/students/list/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        Student.objects.all().delete()
        response2 = self.client.get('/students/list/')
        self.assertEqual(len(response2.data['results']), len(response1.data['results']))

        cache.clear()
        response3 = self.client.get('/students/list/')
        self.assertEqual(len(response3.data['results']), 0)


class StudentUpdatePermissionTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password", role="Admin")
        self.teacher = User.objects.create_user(username="teacher", password="password", role="Teacher")
        self.student_user = User.objects.create_user(username="student", password="password", role="Student")
        self.student = Student.objects.create(user=self.student_user, name="John Doe", email="john@example.com")
        self.update_data = {"name": "Updated Name"}

    def test_admin_can_update_student(self):
        self.client.login(username="admin", password="password")
        response = self.client.put(f'/students/{self.student.id}/', self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_can_update_student(self):
        self.client.login(username="teacher", password="password")
        response = self.client.put(f'/students/{self.student.id}/', self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_update_student(self):
        self.client.login(username="student", password="password")
        response = self.client.put(f'/students/{self.student.id}/', self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StudentDetailApiViewTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="password", role="Admin")
        self.student_user = User.objects.create_user(username="student", password="password", role="Student")
        self.student = Student.objects.create(user=self.student_user, name="John Doe", email="john@example.com")
        self.client.login(username="admin", password="password")

    def test_get_student_detail(self):
        response = self.client.get(f'/students/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "John Doe")
