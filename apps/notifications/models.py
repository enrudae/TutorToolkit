import uuid
from datetime import timedelta
from django.db import models
from django.shortcuts import get_object_or_404
import celery_app
from apps.education_plan.models import EducationPlan
from apps.account.models import UserProfile
from apps.schedule.models import Lesson
from apps.education_plan.services import StudentInvitationService
from apps.notifications.tasks import send_notification
# from apps.notifications.utils import delete_notification


class Notification(models.Model):
    TYPE_CHOICES = (
        ('info', 'INFO'),
        ('invite', 'INVITE'),
        ('canceling', 'CANCELING'),
        ('rescheduling', 'RESCHEDULING')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=200, blank=True)
    content = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notification_task_id = models.CharField(blank=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='not_started')
    education_plan = models.ForeignKey(EducationPlan, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True)
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    @staticmethod
    def create_notification(plan, notification_type, lesson=None, email=None):
        tutor = plan.tutor
        student = plan.student
        notification_task_id = ''
        content = ''

        if notification_type == 'invite' and email:
            student = StudentInvitationService.get_userprofile_by_email(email)
            text = f'Преподаватель {tutor.last_name} {tutor.first_name} приглашает Вас подключиться к дисциплине {plan.discipline}'
            content = plan.invite_code
        elif notification_type == 'info' and lesson:
            notification_time = lesson.date_start - timedelta(hours=3)
            text = f'Урок по предмету {plan.discipline} будет через 3 часа'
            notification_task_id = send_notification.apply_async(args=(student.user.id, text, lesson.id), eta=notification_time)
        elif notification_type == 'rescheduling' and lesson:
            text = f'Урок по предмету {plan.discipline} перенесен на {lesson.date_start.strftime("%d.%m %H:%M")}'
            notification_task_id = send_notification.delay(student.user.id, text, lesson.id)
        elif notification_type == 'canceling' and lesson:
            text = f'Урок по предмету {plan.discipline} {lesson.date_start.strftime("%d.%m %H:%M")} отменен'
            notification_task_id = send_notification.delay(student.user.id, text, lesson.id)
        else:
            raise ValueError("Invalid notification type")

        notification = Notification(
            text=text,
            content=content,
            type=notification_type,
            education_plan=plan,
            lesson=lesson,
            recipient=student,
            notification_task_id=notification_task_id,
        )
        notification.save()
        return notification

    @staticmethod
    def cancel_lesson_notification(lesson):
        if Notification.objects.filter(lesson=lesson).exists():
            notification_for_cancelled = get_object_or_404(Notification, lesson=lesson)
            res = celery_app.delete_task(notification_for_cancelled.notification_task_id)
            print(res)
