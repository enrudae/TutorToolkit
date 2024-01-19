from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import send_notification_according_to_profile_settings
from apps.schedule.models import Lesson

User = get_user_model()


@shared_task
def send_notification(user_id, message):
    user = User.objects.get(id=user_id)
    profile = user.tutor if user.role == 'tutor' else user.student
    send_notification_according_to_profile_settings(profile, message)


@shared_task
def send_lesson_notifications(lesson_id, message):
    lesson = Lesson.objects.get(id=lesson_id)
    student = lesson.education_plan.student
    tutor = lesson.education_plan.tutor

    send_notification_according_to_profile_settings(student, message)
    send_notification_according_to_profile_settings(tutor, message)
