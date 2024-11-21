from django.utils.timezone import now
from django.core.mail import send_mail
from celery import shared_task
import logging

from attendance.models import Attendance
from grades.models import Grade
from students.models import Student

logger = logging.getLogger(__name__)

@shared_task
def send_attendance_reminder(student_name, student_email):
    success_count = 0
    failure_count = 0


    try:
        send_mail(
            subject="Daily Attendance Reminder",
            message=f"Dear {student_name},\n\nYou have not marked your attendance for today. Please log in and mark your attendance now.",
            from_email="altynbek4649@gmail.com",
            recipient_list=[student_email],
        )
        success_count += 1
    except Exception as e:
        logger.error(f"Failed to send email to {student_email}: {e}")
        print(f"Failed to send email to {student_email}: {e}")
        failure_count += 1
        return {"fail": e}
        

    logger.info(f"Attendance reminders sent: {success_count}, failed: {failure_count}")
    return {"success": success_count, "failed": failure_count}


@shared_task
def notify_grade_update(student_id, course_name, grade):
    student = Student.objects.get(id=student_id)
    send_mail(
        subject="Grade Update Notification",
        message=f"Your grade for {course_name} has been updated to {grade}.",
        from_email="altynbek4649@gmail.com",
        recipient_list=[student.email],
    )
    return f"Grade update notification sent to {student.name}."


@shared_task
def generate_daily_report():
    today = now().date()
    attendance_summary = Attendance.objects.filter(date=today).count()
    grades_summary = Grade.objects.filter(date=today).count()

    admin_email = "altynbek4649@gmail.com"
    send_mail(
        subject="Daily Report",
        message=f"Today's Attendance: {attendance_summary}\nGrades Updated: {grades_summary}",
        from_email=admin_email,
        recipient_list=[admin_email],
    )
    return "Daily report sent to admin."


@shared_task
def send_weekly_performance_summary():
    students = Student.objects.all()
    for student in students:
        grades = Grade.objects.filter(student=student)
        summary = "Weekly Performance Summary:\n\n"
        for grade in grades:
            summary += f"{grade.course.name}: {grade.grade}\n"
        send_mail(
            subject="Weekly Performance Summary",
            message=summary,
            from_email="altynbek4649@gmail.com",
            recipient_list=[student.email],
        )
    return f"Weekly summaries sent to {students.count()} students."
