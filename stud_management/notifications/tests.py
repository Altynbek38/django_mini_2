from rest_framework.test import APITestCase
from django.utils.timezone import now
from django.core.mail import outbox
from celery.result import AsyncResult
from .tasks import send_attendance_reminder, notify_grade_update, generate_daily_report, send_weekly_performance_summary
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance
from django.contrib.auth.models import User
from unittest.mock import patch

class CeleryTaskTestCase(APITestCase):
    
    def setUp(self):
        self.student = Student.objects.create(
            name="John Doe", 
            email="john.doe@example.com"
        )

    @patch('django.core.mail.send_mail')  
    def test_send_attendance_reminder_task(self, mock_send_mail):
        result = send_attendance_reminder.apply_async(args=["John Doe", "john.doe@example.com"])

        async_result = AsyncResult(result.id)
        self.assertTrue(async_result.ready()) 
        
        self.assertEqual(mock_send_mail.call_count, 1) 
        mock_send_mail.assert_called_with(
            subject="Daily Attendance Reminder",
            message="Dear John Doe,\n\nYou have not marked your attendance for today. Please log in and mark your attendance now.",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john.doe@example.com"],
        )


    @patch('django.core.mail.send_mail')
    def test_notify_grade_update_task(self, mock_send_mail):
        grade = Grade.objects.create(
            student=self.student,
            course_name="Math 101",
            grade="A",
        )
        
        result = notify_grade_update.apply_async(args=[self.student.id, "Math 101", "A"])
        
        async_result = AsyncResult(result.id)
        self.assertTrue(async_result.ready()) 
        self.assertEqual(mock_send_mail.call_count, 1)  
        
        mock_send_mail.assert_called_with(
            subject="Grade Update Notification",
            message="Your grade for Math 101 has been updated to A.",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john.doe@example.com"],
        )

    @patch('django.core.mail.send_mail') 
    def test_generate_daily_report_task(self, mock_send_mail):
        today = now().date()
        Attendance.objects.create(student=self.student, date=today)
        Grade.objects.create(student=self.student, course_name="Math 101", grade="A", date=today)

        result = generate_daily_report.apply_async()
        
        async_result = AsyncResult(result.id)
        self.assertTrue(async_result.ready())  

        self.assertEqual(mock_send_mail.call_count, 1)  

        mock_send_mail.assert_called_with(
            subject="Daily Report",
            message=f"Today's Attendance: 1\nGrades Updated: 1",
            from_email="altynbek4649@gmail.com",
            recipient_list=["altynbek4649@gmail.com"],
        )

    @patch('django.core.mail.send_mail')
    def test_send_weekly_performance_summary_task(self, mock_send_mail):
        Grade.objects.create(
            student=self.student,
            course_name="Math 101",
            grade="A",
        )

        result = send_weekly_performance_summary.apply_async()
        

        async_result = AsyncResult(result.id)
        self.assertTrue(async_result.ready())
        
        self.assertEqual(mock_send_mail.call_count, 1)  

        mock_send_mail.assert_called_with(
            subject="Weekly Performance Summary",
            message="Weekly Performance Summary:\n\nMath 101: A\n",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john.doe@example.com"],
        )
