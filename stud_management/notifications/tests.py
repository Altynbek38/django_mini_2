from unittest.mock import patch
from django.test import TestCase
from django.utils.timezone import now

from attendance.models import Attendance
from grades.models import Grade
from students.models import Student
from .tasks import (
    send_attendance_reminder,
    notify_grade_update,
    generate_daily_report,
    send_weekly_performance_summary,
)

class CeleryTasksTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="John Doe", email="john@example.com", dob="2000-01-01"
        )

    @patch("django.core.mail.send_mail")
    def test_send_attendance_reminder_success(self, mock_send_mail):
        mock_send_mail.return_value = 1  
        
        result = send_attendance_reminder("John Doe", "john@example.com")
        
        self.assertEqual(result["success"], 1)
        self.assertEqual(result["failed"], 0)
        mock_send_mail.assert_called_once_with(
            subject="Daily Attendance Reminder",
            message="Dear John Doe,\n\nYou have not marked your attendance for today. Please log in and mark your attendance now.",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john@example.com"],
        )

    @patch("django.core.mail.send_mail")
    def test_send_attendance_reminder_failure(self, mock_send_mail):
        mock_send_mail.side_effect = Exception("SMTP Error")  
        
        result = send_attendance_reminder("John Doe", "john@example.com")
        
        self.assertEqual(result["success"], 0)
        self.assertEqual(result["failed"], 1)
        mock_send_mail.assert_called_once()

    @patch("django.core.mail.send_mail")
    def test_notify_grade_update(self, mock_send_mail):
        mock_send_mail.return_value = 1  
        
        result = notify_grade_update(self.student.id, "Math", "A")
        
        self.assertEqual(result, f"Grade update notification sent to {self.student.name}.")
        mock_send_mail.assert_called_once_with(
            subject="Grade Update Notification",
            message=f"Your grade for Math has been updated to A.",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john@example.com"],
        )

    @patch("django.core.mail.send_mail")
    def test_generate_daily_report(self, mock_send_mail):
        Attendance.objects.create(student=self.student, date=now().date())
        Grade.objects.create(student=self.student, course_name="Math", grade="A", date=now().date())
        
        mock_send_mail.return_value = 1  #
        
        result = generate_daily_report()
        
        self.assertEqual(result, "Daily report sent to admin.")
        mock_send_mail.assert_called_once_with(
            subject="Daily Report",
            message=f"Today's Attendance: 1\nGrades Updated: 1",
            from_email="altynbek4649@gmail.com",
            recipient_list=["altynbek4649@gmail.com"],
        )

    @patch("django.core.mail.send_mail")
    def test_send_weekly_performance_summary(self, mock_send_mail):
        Grade.objects.create(student=self.student, course_name="Math", grade="A")
        mock_send_mail.return_value = 1  
        
        result = send_weekly_performance_summary()
        
        self.assertEqual(result, "Weekly summaries sent to 1 students.")
        mock_send_mail.assert_called_once_with(
            subject="Weekly Performance Summary",
            message="Weekly Performance Summary:\n\nMath: A\n",
            from_email="altynbek4649@gmail.com",
            recipient_list=["john@example.com"],
        )
