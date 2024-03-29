import requests
from django.core.mail import send_mail
from celery.result import AsyncResult
from TutorToolkit.settings import EMAIL_HOST_USER, TELEGRAM_BOT_TOKEN


def get_notification_datetime_for_lesson(lesson):
    return lesson.datetime


def send_email_notification(email, message):
    send_mail(
        'Уведомление от TutorToolkit',
        message,
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def send_push_notification(device_id, message):
    pass


def send_telegram_notification(telegram_id, message):
    api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {'chat_id': telegram_id, 'text': message}
    response = requests.post(api_url, params=params)


def send_notification_according_to_profile_settings(profile, message):
    if profile.device_id:
        send_push_notification(profile.device_id, message)
    if profile.receive_email_notifications:
        send_email_notification(profile.user.email, message)
    if profile.telegram_id:
        send_telegram_notification(profile.telegram_id, message)
