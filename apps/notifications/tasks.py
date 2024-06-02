from celery import shared_task
from .utils import send_notification_according_to_profile_settings
from apps.account.models import UserProfile
from apps.schedule.models import Lesson


@shared_task
def send_notification(profile_id, message, lesson_id=None):
    profile = UserProfile.objects.filter(id=profile_id).first()
    if lesson_id:
        lesson = Lesson.objects.get(id=lesson_id)
        if lesson.is_canceled:
            return 'Урок отменен'

    if profile:
        send_notification_according_to_profile_settings(profile, message)
