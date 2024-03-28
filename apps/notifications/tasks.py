from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import send_notification_according_to_profile_settings
from apps.schedule.models import Lesson

User = get_user_model()


@shared_task
def send_notification(user_id, message, lesson_id=None):
    user = User.objects.get(id=user_id)
    profile = user.userprofile
    if lesson_id:
        lesson = Lesson.objects.get(id=lesson_id)
        if lesson.is_canceled:
            return 'Урок отменен'

    send_notification_according_to_profile_settings(profile, message)
