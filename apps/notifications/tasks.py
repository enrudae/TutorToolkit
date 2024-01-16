from celery import shared_task
from .utils import send_email_notification, send_push_notification, send_telegram_notification
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_notification(user_id, message):
    user = User.objects.get(id=user_id)
    profile = user.tutor if user.role == 'tutor' else user.student

    if profile.device_id:
        send_push_notification(profile.device_id, message)
    if profile.receive_email_notifications:
        send_email_notification(profile.user.email, message)
    if profile.telegram_id:
        send_telegram_notification(profile.telegram_id, message)
