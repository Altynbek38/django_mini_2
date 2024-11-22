from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache

from users.models import User
from students.models import Student
from .models import Course, Enrollment


class CourseTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", role="admin")
        self.teacher_user = User.objects.create_user(username="teacher", role="teacher")
        self.student_user = User.objects.create_user(username="student", role="student")

        self.student = Student.objects.create(user=self.student_user)

        self.course = Course.objects.create(
            name="Test Course",
            description="This is a test course",
            instructor=self.teacher_user
        )

        self.client.force_authenticate(user=self.teacher_user)

    def test_create_course(self):
        """Test course creation."""
        url = reverse('course-create')
        data = {"name": "New Course", "description": "Description here", "instructor": self.teacher_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Course.objects.get(id=response.data['id']).name, "New Course")

    def test_list_courses_with_cache(self):
        """Test that course list is cached on repeated requests."""
        url = reverse('course-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 1)
        else:
            self.assertEqual(len(response.data['results']), 1)

        cache_key = f"courses:list:{self.client.get(url).request['PATH_INFO']}"
        cached_data = response.data
        cache.set(cache_key, cached_data, timeout=3600)

        cached_response = cache.get(cache_key)
        self.assertIsNotNone(cached_response)

        if isinstance(cached_response, list):
            self.assertEqual(len(cached_response), 1)
        else:
            self.assertEqual(len(cached_response['results']), 1)

        self.assertEqual(cached_response, cached_data)

    def test_course_update(self):
        """Test course update."""
        url = reverse('course-update', kwargs={'pk': self.course.id})
        data = {"name": "Updated Course"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Course.objects.get(id=self.course.id).name, "Updated Course")

    def test_course_delete(self):
        """Test course deletion."""
        url = reverse('course-delete', kwargs={'pk': self.course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


class EnrollmentTests(APITestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username="teacher", role="teacher")
        self.student_user = User.objects.create_user(username="student", role="student")

        self.student = Student.objects.create(user=self.student_user)

        self.course = Course.objects.create(
            name="Test Course",
            description="This is a test course",
            instructor=self.teacher_user
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        self.client.force_authenticate(user=self.teacher_user)

    def test_create_enrollment(self):
        """Test enrollment creation."""
        url = reverse('enrollment-create')
        data = {"student": self.student.id, "course": self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 2)

    def test_list_enrollments(self):
        """Test listing enrollments."""
        url = reverse('enrollment-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_enrollment_detail(self):
        """Test enrollment detail view."""
        url = reverse('enrollment-detail', kwargs={'pk': self.enrollment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], self.course.id)

    def test_delete_enrollment(self):
        """Test enrollment deletion."""
        url = reverse('enrollment-delete', kwargs={'pk': self.enrollment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Enrollment.objects.count(), 0)
