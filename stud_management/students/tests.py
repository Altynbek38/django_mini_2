from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from students.models import Student
from django.core.cache import cache

class StudentTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", role="admin")
        self.teacher_user = User.objects.create_user(username="teacher", role="teacher")
        self.student_user = User.objects.create_user(username="student", role="student")

        self.student = Student.objects.create(
            user=self.student_user,
            name="John Doe",
            email="john.doe@example.com"
        )

        self.client.force_authenticate(user=self.teacher_user)

    def test_list_students(self):
        """Test listing students."""
        url = reverse('student-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_detail(self):
        """Test retrieving student details."""
        url = reverse('student-detail', kwargs={'pk': self.student.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.student.name)

    def test_student_update(self):
        """Test updating student details."""
        url = reverse('student-update', kwargs={'pk': self.student.id})
        data = {"name": "John Updated"}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Student.objects.get(id=self.student.id).name, "John Updated")

    def test_student_delete(self):
        """Test deleting a student."""
        url = reverse('student-delete', kwargs={'pk': self.student.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Student.objects.count(), 0)

    def test_role_based_permissions(self):
        """Test role-based permissions."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_list_students_with_cache(self):
        """Test that student list is cached on repeated requests."""
        url = reverse('student-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cache_key = f"students:{self.client.get(url).request['PATH_INFO']}"
        cached_data = response.data
        cache.set(cache_key, cached_data, timeout=3600) 

        cached_response = cache.get(cache_key)
        self.assertIsNotNone(cached_response)

        self.assertEqual(cached_response, cached_data)
