from celery import shared_task
from .utils import send_notification_according_to_profile_settings
from apps.account.models import UserProfile
from apps.schedule.models import Lesson
from apps.notifications.models import Notification


@shared_task
def send_notification(profile_id, message, notification_id, lesson_id=None):
    profile = UserProfile.objects.filter(id=profile_id).first()

    notification = Notification.objects.filter(id=notification_id).first()
    if notification:
        notification.is_active = True
        notification.save()

    if lesson_id:
        lesson = Lesson.objects.get(id=lesson_id)
        if lesson.is_canceled:
            return 'Урок отменен'

    if profile:
        send_notification_according_to_profile_settings(profile, message)
